from pathlib import Path

import mne
import numpy as np
import pandas as pd

from pnms import config
from pnms.eeg_features import common_channels, find_bad_channels, load_raw, select_channels, session_features

FIX = Path(__file__).parent / "fixtures"


def _synthetic(n_words=40, sfreq=500.0, seed=0, burst=True):
    rng = np.random.default_rng(seed)
    n_ch, dur = 8, 6.0 * n_words + 10
    data = rng.normal(scale=1e-6, size=(n_ch, int(dur * sfreq)))
    onsets = 5.0 + 6.0 * np.arange(n_words)
    boosted = np.arange(n_words) % 2 == 0
    t = np.arange(int(1.4 * sfreq)) / sfreq
    for on, b in zip(onsets, boosted):
        if b and burst:  # add a 9 Hz burst 0.2-1.6 s after onset on channel 0
            s0 = int((on + 0.2) * sfreq)
            data[0, s0:s0 + len(t)] += 3e-6 * np.sin(2 * np.pi * 9 * t)
    info = mne.create_info([f"E{i + 1}" for i in range(n_ch)], sfreq, "ecog")
    raw = mne.io.RawArray(data, info, verbose="error")
    ev = pd.DataFrame({"trial_type": "WORD", "onset": onsets, "sample": (onsets * sfreq).astype(int)})
    words = ev.assign(trial=1, item_num=np.arange(n_words), serial_pos=np.arange(n_words) + 1)
    return raw, words, ev, boosted


def test_feature_shape_and_zscore():
    raw, words, ev, _ = _synthetic()
    X, names = session_features(raw, words, ev)
    assert X.shape == (40, 8, len(config.FREQS))
    assert names == [f"E{i + 1}" for i in range(8)]
    assert np.allclose(X.mean(axis=0), 0, atol=1e-5)


def test_bad_channels_keep_layout_and_are_zeroed():
    raw, words, ev, _ = _synthetic()
    raw.info["bads"] = ["E8"]  # the last channel, which used to shift the layout
    X, names = session_features(raw, words, ev)
    assert X.shape[1] == 8 and names[-1] == "E8"
    assert np.all(X[:, 7, :] == 0) and np.any(X[:, 6, :] != 0)


def test_feature_tracks_injected_alpha():
    raw, words, ev, boosted = _synthetic(n_words=80)
    X, _ = session_features(raw, words, ev)
    f = int(np.argmin(np.abs(config.FREQS - 8.8)))
    diff = X[boosted, :, f].mean(axis=0) - X[~boosted, :, f].mean(axis=0)
    assert diff[0] > 1.5  # z-units
    assert np.abs(diff[1:]).max() < 1.0  # channels without a burst show only noise


def test_bad_channel_detection():
    raw, *_ = _synthetic(burst=False)
    raw._data[5] *= 100
    assert find_bad_channels(raw) == ["E6"]


def test_channel_types_from_real_sidecar(tmp_path):
    ch = pd.read_csv(FIX / "sub-R1001P_ses-0_task-FR1_acq-bipolar_channels.tsv", sep="\t")
    assert ch["type"].value_counts().to_dict() == {"ECOG": 54, "SEEG": 18}
    info = mne.create_info(list(ch["name"]), 500.0, "misc")
    raw = mne.io.RawArray(np.random.default_rng(0).normal(size=(len(ch), 5000)) * 1e-5, info, verbose="error")
    f = tmp_path / "x_ieeg.fif"
    raw.save(f, verbose="error")
    r = load_raw(f, FIX / "sub-R1001P_ses-0_task-FR1_acq-bipolar_channels.tsv")
    types = r.get_channel_types()
    assert types.count("ecog") == 54 and types.count("seeg") == 18


def test_common_channels_and_selection():
    assert common_channels([["A", "B", "C"], ["C", "A"], ["A", "C", "D"]]) == ["A", "C"]
    X = np.arange(2 * 3 * 1, dtype=float).reshape(2, 3, 1)
    out = select_channels(X, ["A", "B", "C"], ["C", "A"])
    assert out[:, :, 0].tolist() == [[2, 0], [5, 3]]


def test_sampling_rate_too_low_is_refused():
    raw, words, ev, _ = _synthetic(sfreq=256.0)
    import pytest
    with pytest.raises(RuntimeError):
        session_features(raw, words, ev)
