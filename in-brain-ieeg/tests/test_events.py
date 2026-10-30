"""Event parsing on a real RAM FR1 file (sub-R1001P ses-0 of ds004789 v3.1.0).

Expected values were counted directly from the raw file with awk, not with this code:
300 WORD rows in lists 1-25, 12 per list; 53 distinct (list, word) recall pairs match
a word studied in that list; list 2 studied SHEET and recalled SHEET twice and
CLOUD (a list-1 word) twice; 108 REC_WORD rows.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pnms.events import SchemaError, check_sample_alignment, item_number, load_events, schema_report, study_table

FIX = Path(__file__).parent / "fixtures"
EVENTS = FIX / "sub-R1001P_ses-0_task-FR1_events.tsv"


@pytest.fixture(scope="module")
def events():
    return load_events(EVENTS)


@pytest.fixture(scope="module")
def words(events):
    return study_table(events)


def test_session_structure(words):
    assert len(words) == 300
    assert sorted(words["trial"].unique()) == list(range(1, 26))
    assert (words.groupby("trial").size() == 12).all()
    assert (words.groupby("trial")["serial_pos"].apply(list) == [list(range(1, 13))] * 25).all()


def test_recall_labels_match_raw_file(words):
    assert words["recalled"].sum() == 53
    l2 = words[words["trial"] == 2].set_index("item_name")["recalled"]
    assert l2["SHEET"] == 1  # recalled twice, counted once
    assert l2.sum() == 1  # CLOUD was recalled in list 2 but studied in list 1: an intrusion


def test_intrusions_are_reported(events):
    r = schema_report(events)
    assert r["n_recall_rows"] == 108
    assert r["n_recall_rows_not_studied_in_list"] > 0
    assert r["word_pools"] == ["wordpools/wordpool_EN.txt"]


def test_practice_list_excluded(events, words):
    practice = set(events.loc[events["trial_type"] == "PRACTICE_WORD", "item_name"])
    assert practice == {"CHEST", "RING", "COTTON", "CAMEL", "TONGUE", "BEAM", "FLOOD", "WAGON",
                        "IRON", "ATTIC", "WATCH", "RHINO"}
    assert not practice & set(words.loc[words["trial"] == 1, "item_name"])


def test_item_number_is_stable_and_pool_specific():
    assert item_number("wordpools/wordpool_EN.txt", "house") == item_number("wordpools/wordpool_EN.txt", " HOUSE")
    assert item_number("wordpools/wordpool_EN.txt", "HOUSE") != item_number("wordpools/wordpool_SP.txt", "HOUSE")


def test_sample_alignment(events):
    drift = check_sample_alignment(events, 500.0, n_times=2_349_500)  # n_times read from the EDF header
    assert 0 < drift < 0.5
    with pytest.raises(SchemaError):
        check_sample_alignment(events, 500.0, n_times=1_000_000)  # words beyond the end of the file


def test_missing_column_raises(tmp_path):
    p = tmp_path / "e.tsv"
    pd.read_csv(EVENTS, sep="\t").drop(columns=["list"]).to_csv(p, sep="\t", index=False)
    with pytest.raises(SchemaError):
        load_events(p)


def test_duplicate_word_raises(events):
    e = events.copy()
    idx = e.index[e["trial_type"] == "WORD"]
    e.loc[idx[1], "item_name"] = e.loc[idx[0], "item_name"]
    with pytest.raises(SchemaError):
        study_table(e)
