"""Stage 5: group statistics, decision rules and figures (iEEG version: same rule;
the recognition analysis and the eye-channel control do not apply to FR1).

    python scripts/s05_group_stats.py               # confirmatory sample
    python scripts/s05_group_stats.py --pilot       # pilot sample (for checking only)

Secondary 2 (memory strength beyond recall): among words that were NOT recalled
and were tested for recognition, does the held-out EEG-only probability predict a
strong hit ("old" with confidence config.HIGH_CONFIDENCE) over and above the
non-neural probability? One logistic regression per participant,
strong ~ logit(nonneural) + logit(eeg); the eeg slope is tested with Wilcoxon
across people. (The first version used the combined model's probability alone,
which would let serial position and word recallability produce the effect.)
"""
import argparse
import json

import matplotlib
import numpy as np
import statsmodels.api as sm
from scipy import stats as sps

from pnms import config
from pnms.stats import decide, hierarchical_bootstrap_delta, primary_test

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def recognition_slope(d):
    m = (d["y"] == 0) & (d["recog_tested"] == 1)
    if m.sum() < 20:
        return np.nan
    strong = ((d["recog_old"][m] == 1) & (d["recog_conf"][m] >= config.HIGH_CONFIDENCE)).astype(float)
    if strong.min() == strong.max():
        return np.nan
    lg = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))  # noqa: E731
    x = sm.add_constant(np.column_stack([lg(d["nonneural"][m]), lg(d["eeg"][m])]))
    return float(sm.Logit(strong, x).fit(disp=0).params[2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--boot", type=int, default=config.N_BOOTSTRAP)
    ap.add_argument("--replace", nargs="*", default=[], metavar="OLD=NEW",
                    help="registered replacement of a participant with too few usable sessions")
    a = ap.parse_args()
    subs = list(config.PILOT_IDS if a.pilot else config.CONFIRMATORY_IDS)
    for r in a.replace:
        old, new = r.split("=")
        subs[subs.index(old)] = new
    mdir = config.DERIV_DIR / "models"
    res = {s: json.loads((mdir / f"sub-{s}_results.json").read_text()) for s in subs}
    held = {s: dict(np.load(mdir / f"sub-{s}_heldout.npz")) for s in subs}

    delta = np.array([res[s]["delta_auc"] for s in subs])
    primary = primary_test(delta)
    y = {s: held[s]["y"] for s in subs}
    sess = {s: held[s]["session"] for s in subs}
    boot = hierarchical_bootstrap_delta(y, {s: held[s]["combined"] for s in subs},
                                        {s: held[s]["nonneural"] for s in subs}, sess, n_boot=a.boot)
    rboot = hierarchical_bootstrap_delta(y, {s: held[s]["robust_combined"] for s in subs},
                                         {s: held[s]["nonneural"] for s in subs}, sess, n_boot=a.boot)
    decision = decide(primary, boot, rboot)

    sec2 = {"note": "not applicable: FR1 has no recognition test"}

    # Controls (audit, Follow-up 3): eye channels and own-vs-previous-word EEG.
    def paired(a_, b_):
        d = np.array(a_) - np.array(b_)
        return {"mean_difference": float(d.mean()),
                "wilcoxon_p_one_sided": float(sps.wilcoxon(d, alternative="greater").pvalue) if len(d) >= 5 else None}
    controls = {}
    if all("delta_auc_eog" in res[s] for s in subs):
        e = [res[s]["delta_auc_eog"] for s in subs]
        controls["eog"] = {"mean_delta_eog": float(np.mean(e)), "eeg_minus_eog": paired(delta, e)}
    if all("neighbour_test" in res[s] for s in subs):
        own = [res[s]["neighbour_test"]["delta_own"] for s in subs]
        prv = [res[s]["neighbour_test"]["delta_prev"] for s in subs]
        controls["neighbour"] = {"mean_delta_own": float(np.mean(own)), "mean_delta_prev": float(np.mean(prv)),
                                 "own_minus_prev": paired(own, prv)}

    report = {"sample": "pilot" if a.pilot else "confirmatory", "participants": list(subs),
              "primary": primary, "decision": decision, "secondary_recognition": sec2, "controls": controls,
              "per_participant": {s: {k: res[s][k]["auc"] for k in ("nonneural", "eeg", "combined", "robust_combined")
                                      if k in res[s]}
                                  | {"delta_auc": res[s]["delta_auc"], "delta_auc_robust": res[s]["delta_auc_robust"],
                                     "delta_auc_eog": res[s].get("delta_auc_eog"), "eeg_perm_p": res[s]["eeg"].get("perm_p"),
                                     "n_sessions": res[s]["n_sessions"]}
                                  for s in subs}}
    out = config.DERIV_DIR / "group"
    out.mkdir(parents=True, exist_ok=True)
    tag = "pilot" if a.pilot else "confirmatory"
    (out / f"{tag}_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: report[k] for k in ("primary", "decision", "secondary_recognition", "controls")}, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    order = np.argsort(delta)
    for name, mk in (("nonneural", "o"), ("eeg", "s"), ("combined", "^")):
        ax[0].plot(range(len(subs)), [res[subs[i]][name]["auc"] for i in order], mk, label=name)
    ax[0].axhline(0.5, color="grey", lw=0.8)
    ax[0].set(xlabel="participant (sorted by Delta-AUC)", ylabel="held-out AUC", title="Held-out AUC by model")
    ax[0].legend()
    ax[1].plot(range(len(subs)), delta[order], "o")
    ax[1].axhline(0, color="grey", lw=0.8)
    ax[1].axhline(config.SESOI_DELTA_AUC, color="grey", ls="--", lw=0.8)
    ax[1].axhspan(*decision["ci95"], color="C0", alpha=0.15)
    ax[1].set(xlabel="participant", ylabel="Delta-AUC (combined - nonneural)",
              title=f"Delta-AUC, 95% CI band; verdict: {decision['verdict']}")
    fig.tight_layout()
    fig.savefig(out / f"{tag}_auc.png", dpi=150)


if __name__ == "__main__":
    main()
