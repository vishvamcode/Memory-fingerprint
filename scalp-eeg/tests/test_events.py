"""Label derivation, checked on a real PEERS session (sub-LTP063 ses-0, CC0).

Expected values were read directly from the raw TSV (awk on trial_type/trial
columns), independently of the code under test.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pnms.events import SchemaError, check_sample_alignment, load_events, schema_report, study_table

FIX = Path(__file__).parent / "fixtures"
EVENTS = FIX / "sub-LTP063_ses-0_task-ltpFR_events.tsv"


@pytest.fixture(scope="module")
def events():
    return load_events(EVENTS)


@pytest.fixture(scope="module")
def words(events):
    return study_table(events)


def test_session_structure(words):
    assert len(words) == 256
    assert words["trial"].nunique() == 16
    assert (words.groupby("trial").size() == 16).all()
    assert words.groupby("trial")["serial_pos"].apply(lambda s: list(s) == list(range(1, 17))).all()


def test_task_counts(words):
    assert words["task"].value_counts().to_dict() == {1.0: 96, 0.0: 96, -1.0: 64}


def test_list1_recall_labels_match_raw_file(words):
    # REC_WORD rows with trial 1 in the raw file: HELICOPTER OBOE DISHWASHER KNIFE SUPPER PIE CAKE
    l1 = words[words["trial"] == 1].set_index("item_name")["recalled"]
    recalled = {"HELICOPTER", "OBOE", "DISHWASHER", "KNIFE", "SUPPER", "PIE", "CAKE"}
    assert set(l1[l1 == 1].index) == recalled
    assert l1.sum() == 7


def test_session_recall_count(words):
    assert words["recalled"].sum() == 109


def test_intrusions_are_not_labels(events, words):
    # An intrusion (item_num -1) must never mark a studied word as recalled.
    rep = schema_report(events)
    assert rep["n_recall_rows"] == 114
    assert rep["n_recall_rows_not_studied_in_list"] == 3
    rec = events[events["trial_type"] == "REC_WORD"]
    studied = set(zip(words["trial"], words["item_num"]))
    unique_correct = {(int(t), int(n)) for t, n in zip(rec["trial"], rec["item_num"]) if (int(t), int(n)) in studied}
    assert words["recalled"].sum() == len(unique_correct)  # repeats count once


def test_recognition_linked_from_target_rows(words):
    assert words["recog_tested"].sum() == 160
    child = words[words["item_name"] == "CHILD"].iloc[0]
    assert child["recog_old"] == 1 and child["recog_conf"] == 5


def test_stray_recog_resp_on_word_row_is_ignored(events, words):
    # Row 2 of the raw file (WORD 'PIE') carries recog_resp = 1.0; it must not create a recognition label.
    raw_pie = events[(events["trial_type"] == "WORD") & (events["item_name"] == "PIE")].iloc[0]
    assert raw_pie["recog_resp"] == 1.0
    pie = words[words["item_name"] == "PIE"].iloc[0]
    assert pie["recog_tested"] == int(pie["item_num"] in set(
        events.loc[events["trial_type"] == "RECOG_TARGET", "item_num"].astype(int)))


def test_sample_alignment(events):
    assert check_sample_alignment(events, 500.0) < 1e-6
    bad = events.copy()
    bad.loc[bad["trial_type"] == "WORD", "sample"] += 50
    with pytest.raises(SchemaError):
        check_sample_alignment(bad, 500.0)


def test_missing_column_raises(tmp_path):
    df = pd.read_csv(EVENTS, sep="\t").drop(columns=["item_num"])
    p = tmp_path / "x_events.tsv"
    df.to_csv(p, sep="\t", index=False)
    with pytest.raises(SchemaError):
        load_events(p)


def test_duplicate_item_raises(events):
    dup = events.copy()
    idx = dup.index[dup["trial_type"] == "WORD"]
    dup.loc[idx[1], "item_num"] = dup.loc[idx[0], "item_num"]
    with pytest.raises(SchemaError):
        study_table(dup)


def test_practice_lists_excluded(events):
    ev = events.copy()
    w_idx = ev.index[ev["trial_type"] == "WORD"][:16]
    ev.loc[w_idx, "trial"] = 0
    w = study_table(ev)
    assert len(w) == 240 and (w["trial"] >= 1).all()
    assert np.isin(w["trial"].unique(), np.arange(2, 17)).all()
