"""Secondary 1: personal versus pooled EEG decoders.

For each participant, an EEG-only model is trained on all the OTHER participants
in the same sample and applied to all of this participant's words. Its AUC is
compared with the personal EEG-only held-out AUC from s04. Limitation: words in
the test participant's sessions can also occur in other people's training data
(the pool is shared), which the personal model's item hold-out does not allow.

    python scripts/s06_pooled_model.py [--pilot]
"""
import argparse
import json

import numpy as np
from scipy import stats as sps
from sklearn.metrics import roc_auc_score

from pnms import config
from pnms.models import pooled_predict

import s04_fit_models as s04


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    subs = config.PILOT_IDS if a.pilot else config.CONFIRMATORY_IDS
    data = {}
    for s in subs:
        words, E, _, _, _ = s04.load_participant(s)
        data[s] = (E.reshape(len(E), -1), words["recalled"].to_numpy())

    rows = {}
    for s in subs:
        others = [o for o in subs if o != s]
        Xtr = np.vstack([data[o][0] for o in others])
        ytr = np.concatenate([data[o][1] for o in others])
        gtr = np.concatenate([[i] * len(data[o][1]) for i, o in enumerate(others)])
        p = pooled_predict(Xtr, ytr, gtr, data[s][0])
        personal = json.loads((config.DERIV_DIR / "models" / f"sub-{s}_results.json").read_text())["eeg"]["auc"]
        rows[s] = {"pooled_auc": float(roc_auc_score(data[s][1], p)), "personal_auc": personal}
        print(s, rows[s])

    diff = np.array([rows[s]["personal_auc"] - rows[s]["pooled_auc"] for s in subs])
    test = sps.wilcoxon(diff, alternative="two-sided")
    report = {"per_participant": rows, "mean_personal_minus_pooled": float(diff.mean()),
              "wilcoxon_p_two_sided": float(test.pvalue)}
    out = config.DERIV_DIR / "group"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{'pilot' if a.pilot else 'confirmatory'}_pooled.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "per_participant"}, indent=1))


if __name__ == "__main__":
    main()
