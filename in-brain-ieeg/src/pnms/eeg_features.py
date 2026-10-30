"""Label-blind iEEG preprocessing and spectral features for one session.

No step here sees recall labels, so it can run on every session before
any train/test split without leaking outcome information. Recordings are the
dataset's bipolar files (already re-referenced pairwise), so there is no
average reference. Each person has their own electrodes; s04 keeps the channels
present in all of a person's sessions.
"""
from __future__ import annotations

from pathlib import Path

import mne
import numpy as np
import pandas as pd

from . import config
from .events import check_sample_alignment

IEEG_TYPES = {"ECOG": "ecog", "SEEG": "seeg"}
CHANNEL_CHUNK = 16


def load_raw(eeg_path: Path, channels_tsv: Path) -> mne.io.BaseRaw:
    raw = mne.io.read_raw(eeg_path, preload=True, verbose="error")
    ch = pd.read_csv(channels_tsv, sep="\t")
    ch["name"] = ch["name"].astype(str).str.lstrip("﻿")
    types = {n: IEEG_TYPES.get(str(t).upper(), "misc") for n, t in zip(ch["name"], ch["type"]) if n in raw.ch_names}
    raw.set_channel_types(types, verbose="error")
    other = [n for n in raw.ch_names if n not in types]
    if other:
        raw.set_channel_types({n: "misc" for n in other}, verbose="error")
    return raw


def _ieeg_picks(info) -> np.ndarray:
    return mne.pick_types(info, ecog=True, seeg=True, exclude=[])


def find_bad_channels(raw: mne.io.BaseRaw, z_thresh: float = config.BAD_CHANNEL_Z) -> list[str]:
    """Channels whose log-variance is an outlier (robust z, median/MAD across channels)."""
    picks = _ieeg_picks(raw.info)
    logvar = np.log(np.var(raw.get_data(picks=picks), axis=1) + 1e-30)
    med = np.median(logvar)
    mad = np.median(np.abs(logvar - med)) * 1.4826 + 1e-12
    z = (logvar - med) / mad
    names = [raw.ch_names[i] for i in picks]
    return [n for n, zz in zip(names, z) if abs(zz) > z_thresh]


def preprocess(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    nyq = raw.info["sfreq"] / 2
    raw.notch_filter([f for f in config.NOTCH_FREQS if f < nyq], picks="all", verbose="error")
    raw.filter(config.HIGHPASS, None, picks="all", verbose="error")
    raw.info["bads"] = find_bad_channels(raw)
    return raw


def session_features(raw: mne.io.BaseRaw, words: pd.DataFrame, events: pd.DataFrame,
                     n_jobs: int = 1) -> tuple[np.ndarray, list[str]]:
    """Log power (n_words, n_channels, n_freqs), z-scored within session; bad channels set to 0."""
    if raw.info["sfreq"] / 2 <= config.FREQS.max():
        raise RuntimeError(f"sampling rate {raw.info['sfreq']} Hz too low for {config.FREQS.max():.0f} Hz")
    check_sample_alignment(events, raw.info["sfreq"], raw.n_times)
    ev = np.c_[words["sample"].to_numpy(int), np.zeros(len(words), int), np.ones(len(words), int)]
    picks = _ieeg_picks(raw.info)
    epochs = mne.Epochs(raw, ev, tmin=config.EPOCH_TMIN, tmax=config.EPOCH_TMAX, baseline=None,
                        picks=picks, preload=True, reject=None, verbose="error")
    if len(epochs) != len(words):
        raise RuntimeError(f"{len(words) - len(epochs)} epochs were dropped (too close to the file edge?)")
    bads = [n for n in epochs.ch_names if n in raw.info["bads"]]
    epochs.info["bads"] = []
    # Channels in chunks: one session can have >100 channels at 1 kHz, and the full
    # time-frequency array would not fit in memory (a pilot extraction was killed).
    power = []
    for start in range(0, len(epochs.ch_names), CHANNEL_CHUNK):
        chunk = epochs.ch_names[start:start + CHANNEL_CHUNK]
        tfr = epochs.compute_tfr("morlet", freqs=config.FREQS, n_cycles=config.N_CYCLES,
                                 decim=config.TFR_DECIM, return_itc=False, average=False,
                                 picks=chunk, n_jobs=n_jobs, verbose="error")
        t = tfr.times
        win = (t >= config.FEATURE_WINDOW[0]) & (t <= config.FEATURE_WINDOW[1])
        power.append(tfr.get_data()[..., win].mean(axis=-1))
        del tfr
    power = np.concatenate(power, axis=1)  # (words, channels, freqs)
    X = np.log(power)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
    names = list(epochs.ch_names)
    for i, n in enumerate(names):
        if n in bads:
            X[:, i, :] = 0.0
    return X.astype(np.float32), names


def common_channels(channel_lists: list[list[str]]) -> list[str]:
    """Channels present in every session, in the order of the first session."""
    keep = set(channel_lists[0]).intersection(*map(set, channel_lists[1:]))
    return [c for c in channel_lists[0] if c in keep]


def select_channels(X: np.ndarray, channels: list[str], wanted: list[str]) -> np.ndarray:
    idx = {c: i for i, c in enumerate(channels)}
    return X[:, [idx[c] for c in wanted], :]


def save_session(out_path: Path, X: np.ndarray, channels: list[str], words: pd.DataFrame, bads: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_path, X=X, channels=np.array(channels), freqs=config.FREQS,
                        item_num=words["item_num"].to_numpy(), trial=words["trial"].to_numpy(),
                        serial_pos=words["serial_pos"].to_numpy(), bads=np.array(bads, dtype=str))
