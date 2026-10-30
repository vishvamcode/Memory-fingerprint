import numpy as np

from pnms.models import cross_validate, loso_item_splits, permutation_null


def _toy(n_sessions=6, per_session=80, signal=1.0, seed=0):
    rng = np.random.default_rng(seed)
    sessions = np.repeat(np.arange(n_sessions), per_session)
    # Items reused across sessions, never within one, like PEERS.
    items = np.concatenate([rng.permutation(200)[:per_session] for _ in range(n_sessions)])
    y = rng.integers(0, 2, len(sessions))
    X = rng.normal(size=(len(y), 20))
    X[:, 0] += signal * (y - 0.5)
    return X, y, sessions, items


def test_splits_hold_out_sessions_and_items():
    _, _, sessions, items = _toy()
    seen = set()
    for s, train, test in loso_item_splits(sessions, items):
        assert set(sessions[test]) == {s}
        assert s not in set(sessions[train])
        assert not set(items[train]) & set(items[test])
        seen |= set(test)
    assert seen == set(range(len(sessions)))  # every trial is tested exactly once overall


def test_decoder_finds_real_signal():
    X, y, s, i = _toy(signal=1.5)
    assert cross_validate(X, y, s, i).auc(y) > 0.7


def test_decoder_at_chance_without_signal():
    X, y, s, i = _toy(signal=0.0, seed=1)
    assert abs(cross_validate(X, y, s, i).auc(y) - 0.5) < 0.08


def test_item_identity_cannot_leak():
    # Labels are a pure function of item identity and X encodes item identity.
    # Without item hold-out this would be decodable; with it, it must be at chance.
    rng = np.random.default_rng(3)
    sessions = np.repeat(np.arange(6), 50)
    items = np.concatenate([rng.permutation(100)[:50] for _ in range(6)])
    item_label = rng.integers(0, 2, 100)
    y = item_label[items]
    item_code = rng.normal(size=(100, 30))
    X = item_code[items] + 0.1 * rng.normal(size=(len(y), 30))
    assert abs(cross_validate(X, y, sessions, items).auc(y) - 0.5) < 0.1


def test_permutation_null_centred_on_chance():
    X, y, s, i = _toy(signal=1.5, n_sessions=4, per_session=60)
    held = cross_validate(X, y, s, i)
    null = permutation_null(X, y, s, i, strata=s, best_C=held.best_C, n_perm=20, seed=0)
    assert abs(null.mean() - 0.5) < 0.05
    assert held.auc(y) > null.max()


def test_stacked_combined_keeps_behavioural_signal():
    # Strong behavioural predictor + 300 pure-noise EEG features: the stacked
    # combined model must not fall clearly below the behavioural model.
    from pnms.models import cross_validate_stacked
    rng = np.random.default_rng(5)
    sessions = np.repeat(np.arange(6), 100)
    items = np.concatenate([rng.permutation(300)[:100] for _ in range(6)])
    y = rng.integers(0, 2, len(sessions))
    B = rng.normal(size=(len(y), 3)); B[:, 0] += 1.2 * (y - 0.5)
    E = rng.normal(size=(len(y), 300))
    from sklearn.metrics import roc_auc_score
    base = cross_validate(B, y, sessions, items).auc(y)
    comb = roc_auc_score(y, cross_validate_stacked(B, E, y, sessions, items))
    assert comb > base - 0.02


def test_stacked_combined_adds_eeg_signal():
    from pnms.models import cross_validate_stacked
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(6)
    sessions = np.repeat(np.arange(6), 100)
    items = np.concatenate([rng.permutation(300)[:100] for _ in range(6)])
    y = rng.integers(0, 2, len(sessions))
    B = rng.normal(size=(len(y), 3)); B[:, 0] += 0.8 * (y - 0.5)
    E = rng.normal(size=(len(y), 100)); E[:, :5] += 0.6 * (y - 0.5)[:, None]
    base = cross_validate(B, y, sessions, items).auc(y)
    comb = roc_auc_score(y, cross_validate_stacked(B, E, y, sessions, items))
    assert comb > base + 0.03


def test_inner_splits_hold_out_items():
    from pnms.models import inner_splits
    _, _, sessions, items = _toy()
    for tr, te in inner_splits(sessions, items):
        assert not set(sessions[tr]) & set(sessions[te])
        assert not set(items[tr]) & set(items[te])
