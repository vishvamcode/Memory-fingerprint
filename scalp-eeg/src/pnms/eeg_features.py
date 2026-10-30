"""Label-blind EEG preprocessing and spectral features for one session.

No step here sees recall labels, so it can run on every session before
any train/test split without leaking outcome information.
"""
from __future__ import annotations

from pathlib import Path

import mne
import numpy as np
import pandas as pd

from . import config
from .events import check_sample_alignment


def canonical_name(name: str) -> str:
    """'EEG E12' / 'EOG E126' -> 'E12' / 'E126'; 'Cz' -> 'E129' (the EGI reference)."""
    for prefix in ("EEG ", "EOG "):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return config.CHANNEL_ALIASES.get(name, name)


def load_raw(eeg_path: Path, channels_tsv: Path) -> mne.io.BaseRaw:
    raw = mne.io.read_raw(eeg_path, preload=True, verbose="error")
    raw.rename_channels({n: canonical_name(n) for n in raw.ch_names if canonical_name(n) != n})
    ch = pd.read_csv(channels_tsv, sep="\t")
    ch["name"] = ch["name"].astype(str).str.lstrip("\ufeff").map(canonical_name)
    types = {n: t.lower() for n, t in zip(ch["name"], ch["type"]) if n in raw.ch_names and t.upper() != "EEG"}
    raw.set_channel_types(types, verbose="error")
    return raw


def find_bad_channels(raw: mne.io.BaseRaw, z_thresh: float = config.BAD_CHANNEL_Z) -> list[str]:
    """Channels whose log-variance is an outlier (robust z, median/MAD across channels)."""
    picks = mne.pick_types(raw.info, eeg=True)
    logvar = np.log(np.var(raw.get_data(picks=picks), axis=1) + 1e-30)
    med = np.median(logvar)
    mad = np.median(np.abs(logvar - med)) * 1.4826 + 1e-12
    z = (logvar - med) / mad
    names = [raw.ch_names[i] for i in picks]
    return [n for n, zz in zip(names, z) if abs(zz) > z_thresh]


def preprocess(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    raw.notch_filter(list(config.NOTCH_FREQS), picks="all", verbose="error")
    raw.filter(config.HIGHPASS, None, picks="all", verbose="error")
    raw.info["bads"] = find_bad_channels(raw)
    raw.set_eeg_reference("average", verbose="error")  # bad channels are left out of the average
    return raw


def session_features(raw: mne.io.BaseRaw, words: pd.DataFrame, events: pd.DataFrame,
                     n_jobs: int = 1, ch_type: str = "eeg") -> tuple[np.ndarray, list[str]]:
    """Log power (n_words, n_channels, n_freqs), z-scored within session.

    Bad channels are set to 0 (the session mean after z-scoring) so feature
    vectors keep the same layout in every session. ch_type="eog" gives the same
    features for the eye channels, used only as an ocular-artefact control model.
    """
    check_sample_alignment(events, raw.info["sfreq"])
    ev = np.c_[words["sample"].to_numpy(int), np.zeros(len(words), int), np.ones(len(words), int)]
    picks = mne.pick_types(raw.info, eeg=ch_type == "eeg", eog=ch_type == "eog", exclude=[])
    epochs = mne.Epochs(raw, ev, tmin=config.EPOCH_TMIN, tmax=config.EPOCH_TMAX, baseline=None,
                        picks=picks, preload=True, reject=None, verbose="error")
    if len(epochs) != len(words):
        raise RuntimeError(f"{len(words) - len(epochs)} epochs were dropped (too close to the file edge?)")
    bads = [n for n in epochs.ch_names if n in raw.info["bads"]]
    epochs.info["bads"] = []  # keep every channel in the TFR so the layout is fixed; bads are zeroed below
    tfr = epochs.compute_tfr("morlet", freqs=config.FREQS, n_cycles=config.N_CYCLES,
                             decim=config.TFR_DECIM, return_itc=False, average=False,
                             picks="all", n_jobs=n_jobs, verbose="error")
    t = tfr.times
    win = (t >= config.FEATURE_WINDOW[0]) & (t <= config.FEATURE_WINDOW[1])
    power = tfr.get_data(picks="all")[..., win].mean(axis=-1)  # (words, channels, freqs)
    X = np.log(power)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
    names = [epochs.ch_names[i] for i in range(len(epochs.ch_names))]
    for i, n in enumerate(names):
        if n in bads:
            X[:, i, :] = 0.0
    return X.astype(np.float32), names


def peripheral_channels(electrodes_tsv: Path, eeg_names: list[str],
                        fraction: float = config.PERIPHERAL_FRACTION) -> list[str]:
    """Lowest `fraction` of EEG channels by z coordinate in *_electrodes.tsv."""
    el = pd.read_csv(electrodes_tsv, sep="\t").set_index("name")
    z = el.loc[[n for n in eeg_names if n in el.index], "z"].sort_values()
    return list(z.index[: int(round(fraction * len(z)))])


def to_layout(X: np.ndarray, channels: list[str], layout=config.EGI_CHANNELS) -> np.ndarray:
    """Place (words, channels, freqs) features into a fixed channel order; absent channels are 0."""
    out = np.zeros((X.shape[0], len(layout), X.shape[2]), dtype=X.dtype)
    idx = {c: i for i, c in enumerate(layout)}
    names = [canonical_name(str(c)) for c in channels]
    unknown = [c for c in names if c not in idx]
    if unknown:
        raise ValueError(f"channels not in the layout: {unknown[:5]}")
    out[:, [idx[c] for c in names], :] = X
    return out


def save_session(out_path: Path, X: np.ndarray, channels: list[str], words: pd.DataFrame, bads: list[str],
                 X_eog: np.ndarray | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    extra = {} if X_eog is None else {"X_eog": X_eog}
    np.savez_compressed(out_path, X=X, channels=np.array(channels), freqs=config.FREQS, **extra,
                        item_num=words["item_num"].to_numpy(), trial=words["trial"].to_numpy(),
                        serial_pos=words["serial_pos"].to_numpy(), bads=np.array(bads, dtype=str))
