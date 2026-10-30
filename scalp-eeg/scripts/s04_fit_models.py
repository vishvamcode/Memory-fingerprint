"""Stage 4: person-specific decoders for one participant.

Models (all L2 logistic regression, same split):
  nonneural        behavioural and stimulus predictors only
  eeg              EEG features only
  combined         nonneural + EEG score      (primary comparison: combined vs nonneural)
  robust_combined  nonneural + score of EEG <= 30 Hz without peripheral channels
The combined models are stacked: the EEG model's out-of-fold score enters a small
logistic regression next to the behavioural predictors, so the 1,000 EEG features
cannot drown the 24 behavioural ones under one shared penalty. (A single joint
L2 model was tried first on pilot data and was worse than the non-neural model
alone for that reason.)
plus a within-stratum permutation null for the EEG-only model, and two controls
added after the audit (Follow-up 3):
  eog_combined     nonneural + score of the 4 EOG channels' power: if this gains as
                   much as `combined`, the EEG gain is plausibly ocular
  neighbour test   on words at serial position >= 2 only: nonneural + score of the
                   word's OWN EEG vs nonneural + score of the PREVIOUS word's EEG
                   (same list, about 4 s earlier). Equal gains mean the EEG reflects a
                   slow brain state, not the processing of this word.
  --no-task-lists  refit everything on no-task lists only (task == -1), where no
                   key press overlaps the feature window; outputs get a _notask suffix

    python scripts/s04_fit_models.py LTP063 [--perms 200] [--jobs 4] [--no-task-lists]
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from pnms import config
from pnms.behaviour import design_matrix
from pnms.eeg_features import peripheral_channels, to_layout
from pnms.models import cross_validate, cross_validate_stacked, permutation_null


def load_participant(sub):
    words = pd.read_csv(config.DERIV_DIR / "behaviour" / f"sub-{sub}_words.csv")
    feats, eog, keep = [], [], []
    for ses, g in words.groupby("session"):
        f = config.DERIV_DIR / "features" / f"sub-{sub}" / f"ses-{ses}.npz"
        if not f.exists():
            continue
        z = np.load(f)
        # Align feature rows to word rows on (trial, item_num), never by position alone.
        key = pd.MultiIndex.from_arrays([z["trial"], z["item_num"]])
        pos = key.get_indexer(pd.MultiIndex.from_arrays([g["trial"], g["item_num"]]))
        if (pos < 0).any():
            raise RuntimeError(f"ses-{ses}: {(pos < 0).sum()} words have no feature row")
        # Fixed channel order across sessions (EOG channels and EDF names vary; see config).
        feats.append(to_layout(z["X"][pos], list(z["channels"])))
        if "X_eog" not in z or z["X_eog"].shape[1] != 4:
            raise RuntimeError(f"ses-{ses}: EOG features missing or not 4 channels; rerun s03")
        eog.append(z["X_eog"][pos])
        keep.append(g.index.to_numpy())
        channels, freqs = list(config.EGI_CHANNELS), z["freqs"]
    if not feats:
        raise SystemExit(f"no feature files for sub-{sub}; run s03 first")
    words = words.loc[np.concatenate(keep)].reset_index(drop=True)
    return words, np.concatenate(feats), channels, freqs, np.concatenate(eog)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--perms", type=int, default=config.N_PERMUTATIONS)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--no-task-lists", action="store_true")
    a = ap.parse_args()

    words, E, channels, freqs, EOG = load_participant(a.subject)
    if a.no_task_lists:
        keep = (words["task"] == -1).to_numpy()
        words, E, EOG = words[keep].reset_index(drop=True), E[keep], EOG[keep]
    y = words["recalled"].to_numpy()
    ses = words["session"].to_numpy()
    items = words["item_num"].to_numpy()
    B = design_matrix(words).to_numpy()
    eeg = E.reshape(len(E), -1)

    el = sorted((config.DATA_DIR / f"sub-{a.subject}").glob("ses-*/eeg/*_electrodes.tsv"))[0]
    periph = set(peripheral_channels(el, channels))
    ch_ok = np.array([c not in periph for c in channels])
    f_ok = freqs <= config.LOW_FREQ_MAX
    eeg_robust = E[:, ch_ok][:, :, f_ok].reshape(len(E), -1)

    feature_sets = {"nonneural": B, "eeg": eeg}
    results, probas = {}, {}
    for name, X in feature_sets.items():
        held = cross_validate(X, y, ses, items, n_jobs=a.jobs)
        probas[name] = held.proba
        results[name] = {"auc": held.auc(y), "n_features": X.shape[1], "best_C": held.best_C}
        print(f"sub-{a.subject} {name:16s} AUC {results[name]['auc']:.3f} ({X.shape[1]} features)")
        if name == "eeg" and a.perms:
            strata = ses * 100 + words["serial_pos"].to_numpy()
            null = permutation_null(eeg, y, ses, items, strata, held.best_C, a.perms,
                                    seed=config.RANDOM_SEED, n_jobs=a.jobs)
            results[name]["perm_null_mean"] = float(null.mean())
            results[name]["perm_p"] = float((1 + (null >= results[name]["auc"]).sum()) / (1 + len(null)))
            print(f"   permutation null mean {null.mean():.3f}, p = {results[name]['perm_p']:.3f}")
    stacked = [("combined", eeg), ("robust_combined", eeg_robust)]
    if EOG.shape[1]:
        stacked.append(("eog_combined", EOG.reshape(len(EOG), -1)))
    for name, E_ in stacked:
        p = cross_validate_stacked(B, E_, y, ses, items, n_jobs=a.jobs)
        probas[name] = p
        results[name] = {"auc": float(roc_auc_score(y, p)), "n_features": B.shape[1] + E_.shape[1]}
        print(f"sub-{a.subject} {name:16s} AUC {results[name]['auc']:.3f} (stacked: {B.shape[1]} + score of {E_.shape[1]})")
    results["delta_auc"] = results["combined"]["auc"] - results["nonneural"]["auc"]
    results["delta_auc_robust"] = results["robust_combined"]["auc"] - results["nonneural"]["auc"]
    # Neighbour test: previous word in the same list and session.
    w = words.reset_index(drop=True)
    prev = np.full(len(w), -1)
    key = {(r.session, r.trial, r.serial_pos): i for i, r in enumerate(w.itertuples())}
    for i, r in enumerate(w.itertuples()):
        prev[i] = key.get((r.session, r.trial, r.serial_pos - 1), -1)
    m = prev >= 0
    for name, E_ in (("own_eeg_sp2", eeg[m]), ("prev_eeg_sp2", eeg[prev[m]])):
        p = cross_validate_stacked(B[m], E_, y[m], ses[m], items[m], n_jobs=a.jobs)
        results[name] = {"auc": float(roc_auc_score(y[m], p))}
    base_m = float(roc_auc_score(y[m], probas["nonneural"][m]))
    results["neighbour_test"] = {"n_words": int(m.sum()), "nonneural_auc": base_m,
                                 "delta_own": results["own_eeg_sp2"]["auc"] - base_m,
                                 "delta_prev": results["prev_eeg_sp2"]["auc"] - base_m}
    print(f"sub-{a.subject} neighbour test: Delta own {results['neighbour_test']['delta_own']:+.4f}, "
          f"Delta previous word {results['neighbour_test']['delta_prev']:+.4f}")
    if "eog_combined" in results:
        results["delta_auc_eog"] = results["eog_combined"]["auc"] - results["nonneural"]["auc"]
        print(f"sub-{a.subject} Delta-AUC EOG-only control {results['delta_auc_eog']:+.4f}")
    results["n_words"], results["n_sessions"] = int(len(y)), int(len(np.unique(ses)))
    results["peripheral_channels"] = sorted(periph)
    print(f"sub-{a.subject} Delta-AUC {results['delta_auc']:+.4f} (robust {results['delta_auc_robust']:+.4f})")

    out = config.DERIV_DIR / "models"
    out.mkdir(parents=True, exist_ok=True)
    tag = "_notask" if a.no_task_lists else ""
    np.savez_compressed(out / f"sub-{a.subject}_heldout{tag}.npz", y=y, session=ses, item_num=items,
                        recog_tested=words["recog_tested"].to_numpy(),
                        recog_old=words["recog_old"].to_numpy(dtype=float),
                        recog_conf=words["recog_conf"].to_numpy(dtype=float), **probas)
    (out / f"sub-{a.subject}_results{tag}.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
