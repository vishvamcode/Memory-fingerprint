"""Read RAM FR1 event files and derive per-word recall labels.

Like PEERS, the events files have no "recalled" column. A studied word counts as
recalled when the same word appears as a REC_WORD row in the same list (verified
on sub-R1001P ses-0: REC_WORD rows carry the spoken word in item_name and the list
number in `list`; repeats of the same word are counted once). There is no item
number column, so item_num is a stable number derived from (word pool, word).
FR1 has no recognition test; the recognition columns are kept empty so later
stages can share code with the PEERS version.
"""
from __future__ import annotations

import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


class SchemaError(ValueError):
    """The file does not have the structure this analysis was written for."""


def load_events(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", low_memory=False)
    missing = [c for c in config.RAM_REQUIRED_EVENT_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"{path}: missing columns {missing}; found {list(df.columns)}")
    return df


def item_number(pool: str, word: str) -> int:
    """Same word from the same pool -> same number, in every session and participant."""
    return zlib.crc32(f"{pool}|{str(word).strip().upper()}".encode()) & 0x7FFFFFFF


def study_table(events: pd.DataFrame) -> pd.DataFrame:
    """One row per studied word (practice list excluded), with derived labels.

    Columns returned: trial (= list), serial_pos, item_num, item_name, onset, sample,
    recalled, recog_tested, recog_old, recog_conf.
    """
    words = events[(events["trial_type"] == config.STUDY_EVENT) & (events["list"] >= 1)].copy()
    if words.empty:
        raise SchemaError("no study words with list >= 1")
    if words["item_name"].isna().any():
        raise SchemaError("study words with missing item_name")
    words = words.sort_values("sample")
    words["trial"] = words["list"].astype(int)
    words["item_name"] = words["item_name"].astype(str).str.strip().str.upper()
    words["item_num"] = [item_number(p, w) for p, w in zip(words["stim_file"], words["item_name"])]
    if words["item_num"].duplicated().any():
        raise SchemaError("a word occurs twice among study words of one session")
    words["serial_pos"] = words.groupby("trial").cumcount() + 1

    rec = events[events["trial_type"] == config.RECALL_EVENT]
    recalled_pairs = set(zip(rec["list"].astype(int), rec["item_name"].astype(str).str.strip().str.upper()))
    words["recalled"] = [int((t, w) in recalled_pairs) for t, w in zip(words["trial"], words["item_name"])]
    words["recog_tested"] = 0
    words["recog_old"] = np.nan
    words["recog_conf"] = np.nan
    keep = ["trial", "serial_pos", "item_num", "item_name", "onset", "sample",
            "recalled", "recog_tested", "recog_old", "recog_conf"]
    return words[keep].reset_index(drop=True)


def schema_report(events: pd.DataFrame) -> dict:
    """Facts about one session used by the inspection script."""
    w = study_table(events)
    rec = events[events["trial_type"] == config.RECALL_EVENT]
    studied = set(zip(w["trial"], w["item_name"]))
    return {
        "n_rows": len(events),
        "columns": list(events.columns),
        "trial_types": events["trial_type"].value_counts().to_dict(),
        "n_study_words": len(w),
        "n_lists": int(w["trial"].nunique()),
        "words_per_list": sorted(w.groupby("trial").size().unique().tolist()),
        "recall_rate": float(w["recalled"].mean()),
        "n_recall_rows": len(rec),
        "n_recall_rows_not_studied_in_list": int(sum(
            (int(t), str(n).strip().upper()) not in studied for t, n in zip(rec["list"], rec["item_name"]))),
        "word_pools": sorted(events.loc[events["trial_type"] == config.STUDY_EVENT, "stim_file"].dropna().unique()),
    }


def check_sample_alignment(events: pd.DataFrame, sfreq: float, n_times: int) -> float:
    """Checks that study-word samples lie inside the recording and roughly follow onset.

    `sample` is the iEEG-aligned time (see config). Returns the largest drift in
    seconds between (sample - first sample) / sfreq and onset; raises if too large.
    """
    w = events[events["trial_type"] == config.STUDY_EVENT]
    s = w["sample"].to_numpy(float)
    if s.min() < 0 or s.max() >= n_times:
        raise SchemaError(f"study-word samples {s.min():.0f}..{s.max():.0f} outside the recording (0..{n_times})")
    first = events["sample"].iloc[0]
    drift = float(np.abs((w["sample"] - first) / sfreq - (w["onset"] - events["onset"].iloc[0])).max())
    if drift > config.MAX_ONSET_SAMPLE_DRIFT_S:
        raise SchemaError(f"sample and onset columns disagree by {drift:.2f} s")
    return drift
