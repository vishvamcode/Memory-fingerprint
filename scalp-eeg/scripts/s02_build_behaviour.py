"""Stage 2: behavioural tables and the non-neural baseline. No EEG needed.

Needs the event files downloaded by s00. For each pilot and confirmatory
participant it writes derivatives/behaviour/sub-<ID>_words.csv with one row per
studied word, the recall label and all non-neural predictors (item recallability
computed from all OTHER ltpFR participants), then fits the non-neural model with
the same leave-one-session-out, item-held-out split used later for EEG.

    python scripts/s02_build_behaviour.py            # pilot + confirmatory
    python scripts/s02_build_behaviour.py LTP063     # one participant
"""
import json
import sys
from collections import defaultdict

import pandas as pd

from pnms import config
from pnms.behaviour import add_recallability, design_matrix, participant_table
from pnms.models import cross_validate


def main(subjects):
    files = defaultdict(list)
    for p in sorted(config.DATA_DIR.glob(f"sub-*/ses-*/eeg/*_task-{config.TASK}_events.tsv")):
        files[p.name.split("_")[0][4:]].append(p)
    if not files:
        raise SystemExit(f"No event files under {config.DATA_DIR}. Run s00 first.")
    print(f"building word tables for {len(files)} participants")
    all_tables = pd.concat([participant_table(fs) for fs in files.values()], ignore_index=True)

    out_dir = config.DERIV_DIR / "behaviour"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for sub in subjects:
        t = add_recallability(all_tables[all_tables["subject"] == sub].reset_index(drop=True), all_tables)
        t.to_csv(out_dir / f"sub-{sub}_words.csv", index=False)
        X = design_matrix(t).to_numpy()
        y = t["recalled"].to_numpy()
        held = cross_validate(X, y, t["session"].to_numpy(), t["item_num"].to_numpy())
        summary[sub] = {"n_words": len(t), "n_sessions": int(t["session"].nunique()),
                        "recall": float(y.mean()), "auc_nonneural": held.auc(y)}
        print(f"sub-{sub}: {len(t)} words, {summary[sub]['n_sessions']} sessions, "
              f"recall {y.mean():.2f}, non-neural held-out AUC {summary[sub]['auc_nonneural']:.3f}")
    (out_dir / "nonneural_summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or list(config.PILOT_IDS + config.CONFIRMATORY_IDS))
