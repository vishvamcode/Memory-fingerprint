"""Stage 4: person-specific decoders for one participant (iEEG version).

Models (all L2 logistic regression, same split):
  nonneural        behavioural and stimulus predictors only
  eeg              iEEG features only (channels present in all of the person's sessions)
  combined         nonneural + iEEG score     (primary comparison: combined vs nonneural)
  robust_combined  nonneural + score of iEEG <= 30 Hz only
The combined models are stacked exactly as in the PEERS version. Split: one session
x one word group held out (see pnms.models), because every RAM session shows the
same words. Controls kept from the PEERS version: permutation null for the
iEEG-only model and the neighbour test (own vs previous word). Not possible here:
the eye-channel control (no EOG recorded), the no-task-list refit (FR1 has no
encoding task) and the recognition analysis (FR1 has no recognition test).

    python scripts/s04_fit_models.py R1066P [--perms 200] [--jobs 4]
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from pnms import config
from pnms.behaviour import design_matrix
from pnms.eeg_features import common_channels, select_channels
from pnms.models import cross_validate, cross_validate_stacked, permutation_null


def load_participant(sub):
    words = pd.read_csv(config.DERIV_DIR / "behaviour" / f"sub-{sub}_words.csv")
    loaded = {}
    for ses, g in words.groupby("session"):
        f = config.DERIV_DIR / "features" / f"sub-{sub}" / f"ses-{ses}.npz"
        if f.exists():
            loaded[ses] = (g, dict(np.load(f)))
    if len(loaded) < config.MIN_SESSIONS:
        raise SystemExit(f"sub-{sub}: {len(loaded)} sessions with features, fewer than {config.MIN_SESSIONS}; "
                         "participant skipped (registered rule)")
    channels = common_channels([list(z["channels"]) for _, z in loaded.values()])
    feats, keep = [], []
    for ses, (g, z) in loaded.items():
        # Align feature rows to word rows on (trial, item_num), never by position alone.
        key = pd.MultiIndex.from_arrays([z["trial"], z["item_num"]])
        pos = key.get_indexer(pd.MultiIndex.from_arrays([g["trial"], g["item_num"]]))
        if (pos < 0).any():
            raise RuntimeError(f"ses-{ses}: {(pos < 0).sum()} words have no feature row")
        feats.append(select_channels(z["X"][pos], list(z["channels"]), channels))
        keep.append(g.index.to_numpy())
        freqs = z["freqs"]
    words = words.loc[np.concatenate(keep)].reset_index(drop=True)
    return words, np.concatenate(feats), channels, freqs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--perms", type=int, default=config.N_PERMUTATIONS)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()

    words, E, channels, freqs = load_participant(a.subject)
    y = words["recalled"].to_numpy()
    ses = words["session"].to_numpy()
    items = words["item_num"].to_numpy()
    B = design_matrix(words).to_numpy()
    eeg = E.reshape(len(E), -1)

    f_ok = freqs <= config.LOW_FREQ_MAX
    eeg_robust = E[:, :, f_ok].reshape(len(E), -1)

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
    results["n_words"], results["n_sessions"] = int(len(y)), int(len(np.unique(ses)))
    results["n_channels"] = len(channels)
    print(f"sub-{a.subject} Delta-AUC {results['delta_auc']:+.4f} (robust {results['delta_auc_robust']:+.4f})")

    out = config.DERIV_DIR / "models"
    out.mkdir(parents=True, exist_ok=True)
    tag = ""
    np.savez_compressed(out / f"sub-{a.subject}_heldout{tag}.npz", y=y, session=ses, item_num=items,
                        recog_tested=words["recog_tested"].to_numpy(),
                        recog_old=words["recog_old"].to_numpy(dtype=float),
                        recog_conf=words["recog_conf"].to_numpy(dtype=float), **probas)
    (out / f"sub-{a.subject}_results{tag}.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
