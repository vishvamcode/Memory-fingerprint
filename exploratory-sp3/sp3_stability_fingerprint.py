"""SP3 (exploratory) and SP7: is a person's memory signal stable over time, is it
unique to them, and how many sessions does a personal model need?

Uses only the PEERS ltpFR features and word tables already produced by the frozen
first-experiment code (3 pilot + 20 confirmatory participants). Nothing here was
pre-registered: every result is exploratory and must be confirmed on new people.

A  Stability. EEG-only model trained on a person's first N_EARLY sessions, tested on
   each later session (test-session words removed from training). Compared with a
   "recent" model trained on the N_EARLY sessions just before the test session.
   Time = days between the last training session and the test session (scans.tsv).
B  Fingerprint. Per person and per half of sessions (even / odd session numbers),
   a subsequent-memory map: t-statistic recalled vs not recalled for each of the
   1,032 features. Can a person's odd-half map pick out their own even-half map
   among all 23? Control: the same with recall labels shuffled within
   session x serial position (100 shuffles).
C  Data needed (SP7). Train on 1, 2, 4, 8, 16 sessions drawn from the first 16,
   test on each of the person's last 4 sessions.

    python sp3_stability_fingerprint.py --run-dir <run> --scans <dir> --out <dir> [--jobs 2]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.metrics import roc_auc_score

from pnms import config
from pnms.eeg_features import to_layout
from pnms.models import _model, inner_splits

N_EARLY = 6
SIZES = (1, 2, 4, 8, 16)
N_SHUFFLES = 100
SUBJECTS = config.PILOT_IDS + config.CONFIRMATORY_IDS


def load(run, sub):
    words = pd.read_csv(run / "derivatives" / "behaviour" / f"sub-{sub}_words.csv")
    X, keep = [], []
    for ses, g in words.groupby("session"):
        f = run / "derivatives" / "features" / f"sub-{sub}" / f"ses-{ses}.npz"
        if not f.exists():
            continue
        z = np.load(f)
        key = pd.MultiIndex.from_arrays([z["trial"], z["item_num"]])
        pos = key.get_indexer(pd.MultiIndex.from_arrays([g["trial"], g["item_num"]]))
        assert (pos >= 0).all()
        X.append(to_layout(z["X"][pos], list(z["channels"])).reshape(len(g), -1))
        keep.append(g.index.to_numpy())
    words = words.loc[np.concatenate(keep)].reset_index(drop=True)
    return words, np.concatenate(X)


def session_dates(scans, sub):
    out = {}
    for f in Path(scans).glob(f"{sub}_*.tsv"):
        t = pd.read_csv(f, sep="\t")
        t.columns = [c.lstrip("﻿") for c in t.columns]
        out[int(f.stem.split("_")[1])] = pd.to_datetime(t["acq_time"].iloc[0])
    return out


def fit_auc(X, y, ses, items, train_ses, test_ses):
    te = np.flatnonzero(ses == test_ses)
    tr = np.flatnonzero(np.isin(ses, train_ses) & ~np.isin(items, items[te]))
    m = _model(inner_splits(ses[tr], items[tr]))
    m.fit(X[tr], y[tr])
    return float(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]))


def stability(sub, words, X, dates):
    y, ses, items = words["recalled"].to_numpy(), words["session"].to_numpy(), words["item_num"].to_numpy()
    order = sorted(np.unique(ses))
    early = order[:N_EARLY]
    rows = []
    for i, s in enumerate(order[N_EARLY:], start=N_EARLY):
        recent = order[i - N_EARLY:i]
        days = (dates[s] - dates[early[-1]]).total_seconds() / 86400 if s in dates and early[-1] in dates else np.nan
        rows.append({"subject": sub, "test_session": int(s), "days_after_training": days,
                     "auc_early": fit_auc(X, y, ses, items, early, s),
                     "auc_recent": fit_auc(X, y, ses, items, recent, s)})
    return rows


def data_needed(sub, words, X, seed=config.RANDOM_SEED):
    y, ses, items = words["recalled"].to_numpy(), words["session"].to_numpy(), words["item_num"].to_numpy()
    order = sorted(np.unique(ses))
    if len(order) < 20:
        return []
    pool, tests = order[:16], order[-4:]
    rng = np.random.default_rng(seed)
    rows = []
    for n in SIZES:
        for s in tests:
            train = sorted(rng.choice(pool, size=n, replace=False))
            if n == 1:  # inner CV needs 2 groups: split that one session's lists in two
                rows.append({"subject": sub, "n_sessions": n, "test_session": int(s),
                             "auc": fit_auc_single(X, y, ses, items, train[0], s)})
            else:
                rows.append({"subject": sub, "n_sessions": n, "test_session": int(s),
                             "auc": fit_auc(X, y, ses, items, train, s)})
    return rows


def fit_auc_single(X, y, ses, items, train_ses, test_ses):
    te = np.flatnonzero(ses == test_ses)
    tr = np.flatnonzero((ses == train_ses) & ~np.isin(items, items[te]))
    half = np.arange(len(tr)) % 2
    m = _model([(np.flatnonzero(half == 0), np.flatnonzero(half == 1)),
                (np.flatnonzero(half == 1), np.flatnonzero(half == 0))])
    m.fit(X[tr], y[tr])
    return float(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]))


def tmap(X, y):
    a, b = X[y == 1], X[y == 0]
    se = np.sqrt(a.var(0, ddof=1) / len(a) + b.var(0, ddof=1) / len(b)) + 1e-9
    return (a.mean(0) - b.mean(0)) / se


def shuffle_within(y, strata, rng):
    yp = y.copy()
    for g in np.unique(strata):
        idx = np.flatnonzero(strata == g)
        yp[idx] = rng.permutation(yp[idx])
    return yp


def half_maps(words, X, y=None):
    y = words["recalled"].to_numpy() if y is None else y
    odd = (words["session"].to_numpy() % 2 == 1)
    return tmap(X[odd], y[odd]), tmap(X[~odd], y[~odd])


def identification(maps):
    subs = list(maps)
    A = np.array([maps[s][0] for s in subs])
    B = np.array([maps[s][1] for s in subs])
    A = (A - A.mean(1, keepdims=True)) / A.std(1, keepdims=True)
    B = (B - B.mean(1, keepdims=True)) / B.std(1, keepdims=True)
    C = A @ B.T / A.shape[1]
    acc = float(np.mean(C.argmax(1) == np.arange(len(subs))))
    self_r = np.diag(C)
    other_r = (C.sum(1) - self_r) / (len(subs) - 1)
    ranks = [(C[i] > C[i, i]).sum() + 1 for i in range(len(subs))]
    return {"accuracy": acc, "chance": 1 / len(subs), "mean_self_r": float(self_r.mean()),
            "mean_other_r": float(other_r.mean()), "median_self_rank": float(np.median(ranks)),
            "self_r": dict(zip(subs, map(float, self_r)))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--scans", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    data = {s: load(a.run_dir, s) for s in SUBJECTS}
    print("loaded", {s: len(w) for s, (w, _) in data.items()})

    # B: fingerprint (fast)
    maps = {s: half_maps(w, X) for s, (w, X) in data.items()}
    real = identification(maps)
    rng = np.random.default_rng(config.RANDOM_SEED)
    null = []
    for _ in range(N_SHUFFLES):
        sm = {}
        for s, (w, X) in data.items():
            strata = w["session"].to_numpy() * 100 + w["serial_pos"].to_numpy()
            sm[s] = half_maps(w, X, shuffle_within(w["recalled"].to_numpy(), strata, rng))
        null.append(identification(sm)["accuracy"])
    real["shuffled_label_accuracy_mean"] = float(np.mean(null))
    real["shuffled_label_p"] = float((1 + sum(n >= real["accuracy"] for n in null)) / (1 + len(null)))
    (a.out / "fingerprint.json").write_text(json.dumps(real, indent=1))
    print("fingerprint", {k: v for k, v in real.items() if k != "self_r"})

    # A: stability, C: data needed (slow)
    stab = Parallel(n_jobs=a.jobs)(delayed(stability)(s, *data[s], session_dates(a.scans, s)) for s in SUBJECTS)
    st = pd.DataFrame([r for rows in stab for r in rows])
    st.to_csv(a.out / "stability.csv", index=False)
    print(st.groupby("subject")[["auc_early", "auc_recent"]].mean().round(3).to_string())
    need = Parallel(n_jobs=a.jobs)(delayed(data_needed)(s, *data[s]) for s in SUBJECTS)
    nd = pd.DataFrame([r for rows in need for r in rows])
    nd.to_csv(a.out / "data_needed.csv", index=False)
    print(nd.groupby("n_sessions")["auc"].agg(["mean", "std", "count"]).round(3).to_string())


if __name__ == "__main__":
    main()
