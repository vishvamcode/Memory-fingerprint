from pathlib import Path

import mne
import numpy as np
import pandas as pd

from pnms import config
from pnms.eeg_features import find_bad_channels, peripheral_channels, session_features

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
    info = mne.create_info([f"E{i + 1}" for i in range(n_ch)], sfreq, "eeg")
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


def test_peripheral_channels_from_real_layout():
    ch = pd.read_csv(FIX / "sub-LTP063_ses-0_task-ltpFR_channels.tsv", sep="\t")
    eeg = list(ch.loc[ch["type"] == "EEG", "name"])
    per = peripheral_channels(FIX / "sub-LTP063_ses-0_space-CapTrak_electrodes.tsv", eeg)
    assert len(eeg) == 125 and len(per) == round(0.25 * 125)
    el = pd.read_csv(FIX / "sub-LTP063_ses-0_space-CapTrak_electrodes.tsv", sep="\t").set_index("name")
    assert el.loc[per, "z"].max() <= el.loc[[c for c in eeg if c not in per], "z"].min()


def test_eog_features_are_separate():
    raw, words, ev, _ = _synthetic()
    raw.set_channel_types({"E7": "eog", "E8": "eog"}, verbose="error")
    X, names = session_features(raw, words, ev)
    Xe, enames = session_features(raw, words, ev, ch_type="eog")
    assert enames == ["E7", "E8"] and names == [f"E{i + 1}" for i in range(6)]
    assert Xe.shape == (40, 2, len(config.FREQS))


def test_channel_names_are_canonical_and_layout_fixed():
    from pnms.eeg_features import canonical_name, to_layout
    assert canonical_name("EEG E12") == "E12" and canonical_name("EOG E126") == "E126"
    assert canonical_name("Cz") == "E129" and canonical_name("E5") == "E5"
    X = np.arange(2 * 3 * 1, dtype=float).reshape(2, 3, 1) + 1
    a = to_layout(X, ["E1", "E25", "E129"])
    b = to_layout(X[:, [0, 2, 1]], ["E1", "Cz", "EEG E25"])  # other order, other names
    assert a.shape == (2, 129, 1) and np.array_equal(a, b)
    assert a[:, 25, 0].tolist() == [0, 0]  # E26 absent -> 0
