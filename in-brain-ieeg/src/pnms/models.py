"""Cross-validated decoders with session and item hold-out.

Outer loop: leave one session x one word group out (iEEG version: every session
shows the same words). Training data never contain a word (item_num) of the test set. Scaling and the penalty strength
are fitted on training data only. The inner folds (penalty choice and the
out-of-fold EEG scores of the stacked model) apply the same rule: grouped by
session, with inner-test words removed from inner training.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, GroupKFold  # GroupKFold: pooled_predict only
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import config


def word_folds(items: np.ndarray, k: int = config.WORD_FOLDS) -> np.ndarray:
    """Fixed word group (0..k-1) for every trial; the same word always gets the same group."""
    items = np.asarray(items)
    uniq = np.unique(items)
    order = np.random.default_rng(config.RANDOM_SEED).permutation(len(uniq))
    fold_of = dict(zip(uniq[order], np.arange(len(uniq)) % k))
    return np.array([fold_of[i] for i in items])


def loso_item_splits(sessions: np.ndarray, items: np.ndarray):
    """Yield (key, train_idx, test_idx), key = session * 100 + word group.

    Test = one session x one word group. Train = other sessions AND other word
    groups, so no test word and no test-session trial is ever in training (every
    RAM session shows the same 300 words, so a session hold-out alone is not enough).
    """
    sessions, items = np.asarray(sessions), np.asarray(items)
    folds = word_folds(items)
    for s in np.unique(sessions):
        for k in np.unique(folds):
            test = np.flatnonzero((sessions == s) & (folds == k))
            train = np.flatnonzero((sessions != s) & (folds != k) & ~np.isin(items, items[test]))
            if len(test) and len(train):
                yield int(s) * 100 + int(k), train, test


def inner_splits(sessions: np.ndarray, items: np.ndarray,
                 min_test: int = config.MIN_INNER_TEST) -> list[tuple[np.ndarray, np.ndarray]]:
    """Inner folds with the same rule: test = session x word group; training never holds a
    test word, and never the test session unless only one session is left. Folds with
    fewer than `min_test` words are dropped for penalty tuning (a short session can leave a
    fold of about 10 words, sometimes with no recalled word, which makes its AUC undefined).
    The stacked model's out-of-fold scores use min_test=0, so every row gets a score."""
    sessions, items = np.asarray(sessions), np.asarray(items)
    folds = word_folds(items)
    several = len(np.unique(sessions)) > 1
    out = []
    for s in np.unique(sessions):
        for k in np.unique(folds):
            te = np.flatnonzero((sessions == s) & (folds == k))
            tr = np.flatnonzero((folds != k) & ((sessions != s) if several else True) & ~np.isin(items, items[te]))
            if len(te) and len(tr):
                out.append((tr, te))
    big = [f for f in out if len(f[1]) >= min_test]
    return big or out  # tiny data (unit tests): keep every fold rather than none


def _model(cv) -> GridSearchCV:
    pipe = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000))
    return GridSearchCV(pipe, {"logisticregression__C": config.C_GRID}, scoring="roc_auc", cv=cv, n_jobs=1)


def _fold(X, y, sessions, items, train, test):
    m = _model(inner_splits(sessions[train], items[train]))
    m.fit(X[train], y[train])
    return test, m.predict_proba(X[test])[:, 1], m.best_params_["logisticregression__C"]


@dataclass
class HeldOut:
    proba: np.ndarray  # held-out predicted probability for every trial
    best_C: dict  # test session -> chosen C

    def auc(self, y: np.ndarray) -> float:
        return float(roc_auc_score(y, self.proba))


def cross_validate(X: np.ndarray, y: np.ndarray, sessions: np.ndarray, items: np.ndarray,
                   n_jobs: int = 1) -> HeldOut:
    splits = list(loso_item_splits(sessions, items))
    res = Parallel(n_jobs=n_jobs)(delayed(_fold)(X, y, sessions, items, tr, te) for _, tr, te in splits)
    proba = np.full(len(y), np.nan)
    best = {}
    for (s, _, _), (te, p, c) in zip(splits, res):
        proba[te] = p
        best[int(s)] = float(c)
    return HeldOut(proba, best)


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _stacked_fold(B, E, y, sessions, items, train, test):
    """Combined model without letting 1,000 EEG features swamp the behavioural ones.

    1. Inner out-of-fold EEG scores on the training set (inner_splits, item hold-out).
    2. Low-dimensional logistic regression on [behaviour, EEG score] (weak penalty).
    3. EEG model refit on all training data supplies the test-set EEG score.
    """
    tr_ses, tr_items = sessions[train], items[train]
    Et, yt = E[train], y[train]
    oof = np.full(len(train), np.nan)
    for itr, ite in inner_splits(tr_ses, tr_items, min_test=0):
        m = _model(inner_splits(tr_ses[itr], tr_items[itr]))
        m.fit(Et[itr], yt[itr])
        oof[ite] = m.predict_proba(Et[ite])[:, 1]
    if np.isnan(oof).any():
        raise RuntimeError("inner folds left training rows without an out-of-fold score")
    eeg = _model(inner_splits(tr_ses, tr_items))
    eeg.fit(Et, yt)
    test_score = eeg.predict_proba(E[test])[:, 1]
    top = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000))
    top.fit(np.column_stack([B[train], _logit(oof)]), y[train])
    return test, top.predict_proba(np.column_stack([B[test], _logit(test_score)]))[:, 1]


def cross_validate_stacked(B: np.ndarray, E: np.ndarray, y: np.ndarray, sessions: np.ndarray,
                           items: np.ndarray, n_jobs: int = 1) -> np.ndarray:
    """Held-out probabilities of the stacked combined model (same outer split as cross_validate)."""
    splits = list(loso_item_splits(sessions, items))
    res = Parallel(n_jobs=n_jobs)(delayed(_stacked_fold)(B, E, y, sessions, items, tr, te) for _, tr, te in splits)
    proba = np.full(len(y), np.nan)
    for te, p in res:
        proba[te] = p
    return proba


def permutation_null(X, y, sessions, items, strata, best_C: dict, n_perm: int, seed: int,
                     n_jobs: int = 1) -> np.ndarray:
    """Held-out AUCs after shuffling labels within strata (e.g. session x serial position).

    For speed the penalty per fold is fixed at the value chosen on the real labels.
    """
    rng = np.random.default_rng(seed)
    splits = list(loso_item_splits(sessions, items))

    def one(perm_seed):
        r = np.random.default_rng(perm_seed)
        yp = y.copy()
        for g in np.unique(strata):
            idx = np.flatnonzero(strata == g)
            yp[idx] = r.permutation(yp[idx])
        proba = np.full(len(y), np.nan)
        for s, tr, te in splits:
            m = make_pipeline(StandardScaler(), LogisticRegression(
                C=best_C[int(s)], class_weight="balanced", max_iter=2000))
            m.fit(X[tr], yp[tr])
            proba[te] = m.predict_proba(X[te])[:, 1]
        return roc_auc_score(yp, proba)

    seeds = rng.integers(0, 2**32 - 1, size=n_perm)
    return np.array(Parallel(n_jobs=n_jobs)(delayed(one)(s) for s in seeds))


def pooled_predict(X_train: np.ndarray, y_train: np.ndarray, groups_train: np.ndarray,
                   X_test: np.ndarray) -> np.ndarray:
    """Model trained on other participants (groups = participant) applied to new data."""
    k = min(config.INNER_FOLDS, len(np.unique(groups_train)))
    m = _model(list(GroupKFold(n_splits=k).split(X_train, groups=groups_train)))
    m.fit(X_train, y_train)
    return m.predict_proba(X_test)[:, 1]
