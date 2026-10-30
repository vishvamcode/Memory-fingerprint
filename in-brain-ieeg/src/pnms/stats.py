"""Group-level statistics for the pre-registered decision rules."""
from __future__ import annotations

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score

from . import config


def hierarchical_bootstrap_delta(y: dict, p_full: dict, p_base: dict, sessions: dict,
                                 n_boot: int = config.N_BOOTSTRAP, seed: int = config.RANDOM_SEED,
                                 ) -> np.ndarray:
    """Bootstrap distribution of mean Delta-AUC.

    Resample participants with replacement, then sessions within each participant,
    recompute each participant's pooled held-out AUCs, and average Delta-AUC.
    All dict arguments are keyed by participant id with per-trial arrays.
    """
    rng = np.random.default_rng(seed)
    subs = list(y)
    out = np.empty(n_boot)
    for b in range(n_boot):
        deltas = []
        for s in rng.choice(subs, size=len(subs), replace=True):
            ses = np.unique(sessions[s])
            pick = rng.choice(ses, size=len(ses), replace=True)
            idx = np.concatenate([np.flatnonzero(sessions[s] == k) for k in pick])
            yy = y[s][idx]
            if yy.min() == yy.max():
                continue
            deltas.append(roc_auc_score(yy, p_full[s][idx]) - roc_auc_score(yy, p_base[s][idx]))
        out[b] = np.mean(deltas)
    return out


def primary_test(delta_auc: np.ndarray) -> dict:
    """One-sided Wilcoxon signed-rank test of Delta-AUC > 0 across participants."""
    w = stats.wilcoxon(delta_auc, alternative="greater")
    return {"n": int(len(delta_auc)), "mean": float(np.mean(delta_auc)),
            "median": float(np.median(delta_auc)), "wilcoxon_W": float(w.statistic),
            "p_one_sided": float(w.pvalue)}


def equivalence_upper(boot: np.ndarray, sesoi: float = config.SESOI_DELTA_AUC, level: float = 0.90) -> dict:
    """Failure rule: the 90% CI of mean Delta-AUC lies entirely below the SESOI."""
    lo, hi = np.quantile(boot, [(1 - level) / 2, 1 - (1 - level) / 2])
    return {"ci90": (float(lo), float(hi)), "below_sesoi": bool(hi < sesoi)}


def decide(primary: dict, boot: np.ndarray, robust_boot: np.ndarray,
           sesoi: float = config.SESOI_DELTA_AUC, alpha: float = config.ALPHA) -> dict:
    """Apply the decision rules exactly as written in the pre-registration."""
    ci95 = np.quantile(boot, [0.025, 0.975])
    robust_ci95 = np.quantile(robust_boot, [0.025, 0.975])
    eq = equivalence_upper(boot, sesoi)
    success = (primary["p_one_sided"] < alpha and ci95[0] > 0 and primary["mean"] >= sesoi
               and robust_ci95[0] > 0)
    failure = eq["below_sesoi"]
    verdict = "success" if success else "failure" if failure else "ambiguous"
    # A failure whose 95% CI also excludes 0 means: information is present but too small to use.
    present_but_negligible = bool(failure and ci95[0] > 0)
    return {"verdict": verdict, "present_but_negligible": present_but_negligible,
            "ci95": ci95.tolist(), "robust_ci95": robust_ci95.tolist(), **eq}


def holm(pvalues: dict) -> dict:
    """Holm-adjusted p-values for the secondary family."""
    keys = sorted(pvalues, key=pvalues.get)
    m, running, out = len(keys), 0.0, {}
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (m - i) * pvalues[k]))
        out[k] = running
    return out
