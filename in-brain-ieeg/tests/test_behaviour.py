import numpy as np
import pandas as pd
import pytest

from pnms.behaviour import add_recallability, design_matrix, item_recallability, participant_table
from tests.test_events import EVENTS


def _table(sub, sessions):
    rows = []
    for ses, items, recalled in sessions:
        for i, (n, r) in enumerate(zip(items, recalled)):
            rows.append(dict(subject=sub, session=ses, trial=1, serial_pos=i + 1, item_num=n,
                             item_name="W" * (n % 7 + 1), task=-1, onset=float(i), recalled=r))
    t = pd.DataFrame(rows)
    t["prior_exposures"] = t.groupby("item_num").cumcount()
    t["word_length"] = t["item_name"].str.len()
    return t


def test_participant_table_on_real_file(tmp_path):
    # The same real session saved under two session numbers: every word's second
    # appearance must have prior_exposures == 1.
    for ses in (0, 1):
        (tmp_path / f"sub-R1001P_ses-{ses}_task-FR1_events.tsv").write_bytes(EVENTS.read_bytes())
    t = participant_table(sorted(tmp_path.glob("*.tsv")))
    assert len(t) == 600
    assert (t.loc[t["session"] == 0, "prior_exposures"] == 0).all()
    assert (t.loc[t["session"] == 1, "prior_exposures"] == 1).all()
    assert t.loc[t["item_name"] == "BRIDGE", "word_length"].iloc[0] == 6


def test_recallability_excludes_own_data():
    a = _table("A", [(0, [1, 2], [1, 1])])  # A always recalls items 1, 2
    b = _table("B", [(0, [1, 2], [0, 0])])  # B never does
    all_t = pd.concat([a, b], ignore_index=True)
    ra = add_recallability(a, all_t)
    # Estimated only from B (all zeros), shrunk toward B's mean (0): must be 0, not influenced by A.
    assert np.allclose(ra["item_recallability"], 0.0)


def test_recallability_shrinkage():
    others = _table("B", [(0, [1, 2, 3, 4], [1, 1, 0, 0])])
    r = item_recallability(others, prior_weight=5.0)
    assert r[1] == pytest.approx((1 + 5 * 0.5) / (1 + 5))
    assert r[3] == pytest.approx((0 + 5 * 0.5) / (1 + 5))


def test_design_matrix_columns():
    t = _table("A", [(0, list(range(1, 17)), [0] * 16)])
    t["item_recallability"] = 0.5
    X = design_matrix(t)
    assert [c for c in X.columns if c.startswith("sp_")] == [f"sp_{i}" for i in range(1, 17)]
    assert {"task_-1", "task_0", "task_1", "list_number", "session_number", "prior_exposures",
            "word_length", "item_recallability"} <= set(X.columns)
    assert not [c for c in X.columns if c.startswith("list_") and c != "list_number"]  # one list only
    t2 = t.assign(trial=[1] * 8 + [2] * 8)
    assert design_matrix(t2)["list_2"].tolist() == [0.0] * 8 + [1.0] * 8
    assert "recalled" not in X.columns
    assert X.notna().all().all()
