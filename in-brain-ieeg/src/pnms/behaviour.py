"""Non-neural predictors of recall.

Every predictor here is computable without EEG and without the outcome of the
trial being predicted. Item recallability uses other participants only.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .events import SchemaError, load_events, study_table

EVENTS_RE = re.compile(r"sub-(?P<sub>\w+?)_ses-(?P<ses>\d+)_task-(?P<task>\w+?)_events\.tsv$")


def participant_table(event_files: list[Path]) -> pd.DataFrame:
    """Stack study tables of one participant's sessions and add exposure counts."""
    parts = []
    for f in event_files:
        m = EVENTS_RE.search(Path(f).name)
        if not m:
            raise ValueError(f"unexpected file name {f}")
        try:
            t = study_table(load_events(f))
        except SchemaError:  # logged by s00 (session_summary.csv); same skip rule as s03
            continue
        t.insert(0, "session", int(m["ses"]))
        t.insert(0, "subject", m["sub"])
        parts.append(t)
    df = pd.concat(parts, ignore_index=True).sort_values(["session", "onset"]).reset_index(drop=True)
    # How many times this person saw the word before this trial (earlier sessions only,
    # since a word never repeats within a session).
    df["prior_exposures"] = df.groupby("item_num").cumcount()
    df["word_length"] = df["item_name"].astype(str).str.len()
    return df


def item_recallability(others: pd.DataFrame, prior_weight: float = config.RECALLABILITY_PRIOR_WEIGHT) -> pd.Series:
    """Recall rate per item_num from OTHER participants, shrunk toward their mean.

    rate = (recalled + w * mean) / (n + w)
    """
    grand = others["recalled"].mean()
    g = others.groupby("item_num")["recalled"].agg(["sum", "count"])
    return (g["sum"] + prior_weight * grand) / (g["count"] + prior_weight)


def add_recallability(table: pd.DataFrame, all_tables: pd.DataFrame) -> pd.DataFrame:
    """Attach recallability computed without this participant's data."""
    subject = table["subject"].iloc[0]
    others = all_tables[all_tables["subject"] != subject]
    if others.empty:
        raise ValueError("need other participants to estimate item recallability")
    rates = item_recallability(others)
    out = table.copy()
    out["item_recallability"] = out["item_num"].map(rates).fillna(others["recalled"].mean())
    return out


def design_matrix(table: pd.DataFrame) -> pd.DataFrame:
    """Numeric non-neural predictors, fixed in advance (Section 10 of the report)."""
    X = pd.DataFrame(index=table.index)
    for sp in range(1, int(table["serial_pos"].max()) + 1):
        X[f"sp_{sp}"] = (table["serial_pos"] == sp).astype(float)
    if "task" in table.columns:
        for lvl in config.LTPFR_TASK_LEVELS:
            X[f"task_{lvl}"] = (table["task"] == lvl).astype(float)
    X["list_number"] = table["trial"].astype(float)
    # One indicator per list as well, so a non-linear time-on-task (fatigue) curve is in
    # the baseline and cannot be credited to slow EEG drift (added after the audit).
    for li in range(2, int(table["trial"].max()) + 1):
        X[f"list_{li}"] = (table["trial"] == li).astype(float)
    X["session_number"] = table["session"].astype(float)
    X["prior_exposures"] = table["prior_exposures"].astype(float)
    X["word_length"] = table["word_length"].astype(float)
    X["item_recallability"] = table["item_recallability"].astype(float)
    return X
