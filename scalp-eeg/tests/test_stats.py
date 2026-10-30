import numpy as np
import pytest

from pnms.stats import decide, hierarchical_bootstrap_delta, holm, primary_test


def test_holm():
    adj = holm({"a": 0.01, "b": 0.04})
    assert adj["a"] == pytest.approx(0.02) and adj["b"] == pytest.approx(0.04)


def _boot(center, spread=0.002, n=2000):
    return np.random.default_rng(0).normal(center, spread, n)


def test_decide_success():
    p = primary_test(np.full(20, 0.02) + np.linspace(-0.001, 0.001, 20))
    assert decide(p, _boot(0.02), _boot(0.015))["verdict"] == "success"


def test_decide_failure_by_equivalence():
    p = primary_test(np.linspace(-0.005, 0.006, 20))
    assert decide(p, _boot(0.0005), _boot(0.0))["verdict"] == "failure"


def test_decide_ambiguous_when_artefact_model_fails():
    p = primary_test(np.full(20, 0.02) + np.linspace(-0.001, 0.001, 20))
    assert decide(p, _boot(0.02), _boot(0.0))["verdict"] == "ambiguous"


def test_small_but_real_counts_as_failure_flagged_present():
    p = primary_test(np.full(20, 0.005) + np.linspace(-0.001, 0.001, 20))
    d = decide(p, _boot(0.005, 0.0005), _boot(0.005, 0.0005))
    assert d["verdict"] == "failure" and d["present_but_negligible"]


def test_ambiguous_when_underpowered():
    p = primary_test(np.linspace(-0.02, 0.03, 20))
    assert decide(p, _boot(0.005, 0.01), _boot(0.005, 0.01))["verdict"] == "ambiguous"


def test_bootstrap_recovers_known_delta():
    rng = np.random.default_rng(1)
    y, pf, pb, ses = {}, {}, {}, {}
    for s in range(8):
        yy = rng.integers(0, 2, 400)
        y[s] = yy
        pb[s] = rng.random(400)                    # useless baseline (AUC about 0.5)
        pf[s] = 0.6 * yy + rng.random(400)          # informative model
        ses[s] = np.repeat(np.arange(4), 100)
    b = hierarchical_bootstrap_delta(y, pf, pb, ses, n_boot=200, seed=0)
    assert 0.2 < b.mean() < 0.45 and b.std() < 0.05
