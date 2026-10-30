"""Read PEERS event files and derive per-word memory labels.

The events files have no "recalled" column. A studied word counts as recalled
when the same (trial, item_num) pair appears as a REC_WORD row in the same
session. Recognition results are stored on the RECOG_TARGET row itself
(recog_resp: 1 old / 0 new; recog_conf: 1-5), as verified on sub-LTP063.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config


class SchemaError(ValueError):
    """The file does not have the structure this analysis was written for."""


def load_events(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", low_memory=False)
    missing = [c for c in config.REQUIRED_EVENT_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"{path}: missing columns {missing}; found {list(df.columns)}")
    return df


def study_table(events: pd.DataFrame) -> pd.DataFrame:
    """One row per studied word (practice lists excluded), with derived labels.

    Columns returned: trial, serial_pos, item_num, item_name, task (if present),
    onset, sample, recalled, recog_tested, recog_old, recog_conf.
    """
    words = events[(events["trial_type"] == config.STUDY_EVENT) & (events["trial"] >= 1)].copy()
    if words.empty:
        raise SchemaError("no study words with trial >= 1")
    if words["item_num"].isna().any() or (words["item_num"] < 0).any():
        raise SchemaError("study words with missing or negative item_num")
    if words["item_num"].duplicated().any():
        raise SchemaError("an item_num occurs twice among study words of one session")

    words = words.sort_values("onset")
    words["trial"] = words["trial"].astype(int)
    words["item_num"] = words["item_num"].astype(int)
    words["serial_pos"] = words.groupby("trial").cumcount() + 1

    rec = events[events["trial_type"] == config.RECALL_EVENT]
    recalled_pairs = set(zip(rec["trial"].dropna().astype(int), rec["item_num"].dropna().astype(int)))
    words["recalled"] = [int((t, n) in recalled_pairs) for t, n in zip(words["trial"], words["item_num"])]

    targets = events[events["trial_type"] == config.RECOG_TARGET_EVENT]
    targets = targets.dropna(subset=["item_num"]).drop_duplicates("item_num")
    tmap = targets.set_index(targets["item_num"].astype(int))
    words["recog_tested"] = words["item_num"].isin(tmap.index).astype(int)
    words["recog_old"] = words["item_num"].map(tmap["recog_resp"]) if "recog_resp" in tmap else np.nan
    words["recog_conf"] = words["item_num"].map(tmap["recog_conf"]) if "recog_conf" in tmap else np.nan

    keep = ["trial", "serial_pos", "item_num", "item_name", "onset", "sample",
            "recalled", "recog_tested", "recog_old", "recog_conf"]
    if "task" in words.columns:
        keep.insert(4, "task")
    return words[keep].reset_index(drop=True)


def schema_report(events: pd.DataFrame) -> dict:
    """Facts about one session used by the inspection script."""
    w = study_table(events)
    report = {
        "n_rows": len(events),
        "columns": list(events.columns),
        "trial_types": events["trial_type"].value_counts().to_dict(),
        "n_study_words": len(w),
        "n_lists": int(w["trial"].nunique()),
        "words_per_list": sorted(w.groupby("trial").size().unique().tolist()),
        "recall_rate": float(w["recalled"].mean()),
        "n_recog_tested": int(w["recog_tested"].sum()),
        "has_task_column": "task" in w.columns,
        "sample_matches_onset": None,
    }
    if "task" in w.columns:
        report["task_counts"] = w["task"].value_counts().to_dict()
    # Recall rows that do not match a studied word in their list are intrusions or vocalisations.
    rec = events[events["trial_type"] == config.RECALL_EVENT]
    studied = set(zip(w["trial"], w["item_num"]))
    report["n_recall_rows"] = len(rec)
    report["n_recall_rows_not_studied_in_list"] = int(
        sum((int(t), int(n)) not in studied for t, n in zip(rec["trial"].fillna(-1), rec["item_num"].fillna(-1)))
    )
    return report


def check_sample_alignment(events: pd.DataFrame, sfreq: float, tol_samples: float = 1.0) -> float:
    """Largest |onset * sfreq - sample| over study words; raises if above tolerance."""
    w = events[events["trial_type"] == config.STUDY_EVENT]
    err = float(np.abs(w["onset"] * sfreq - w["sample"]).max())
    if err > tol_samples:
        raise SchemaError(f"sample column disagrees with onset by {err:.2f} samples")
    return err
