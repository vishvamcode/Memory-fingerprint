"""Fixed analysis settings.

Everything a reviewer could suspect of being tuned on the test data lives here.
Change values only before the pre-registration is posted; after that, any change
must be reported together with the original result.
"""
import os
from pathlib import Path

import numpy as np

# --- dataset -----------------------------------------------------------------
DATASET_ID = "ds004395"
DATASET_VERSION = "2.0.0"  # dataset_description.json DatasetDOI: doi:10.18112/openneuro.ds004395.v2.0.0
S3_ROOT = f"https://s3.amazonaws.com/openneuro.org/{DATASET_ID}"
TASK = "ltpFR"

# Local folders. Override with the PNMS_DATA / PNMS_DERIV environment variables.
DATA_DIR = Path(os.environ.get("PNMS_DATA", "data")).resolve()
DERIV_DIR = Path(os.environ.get("PNMS_DERIV", "derivatives")).resolve()

# --- event schema (verified on the real files, 21 Oct 2026) -------------------
STUDY_EVENT = "WORD"
RECALL_EVENT = "REC_WORD"
RECOG_TARGET_EVENT = "RECOG_TARGET"
# EGI HydroCel 129 layout. Features are stored in this fixed order in every session,
# because which channels are EOG (E25 or E26) and how the EDF names channels
# ("E1" or "EEG E1"; reference "E129" or "Cz") differ between sessions (seen in
# sub-LTP063 ses-1, ses-5, ses-8 and sub-LTP065 ses-7).
EGI_CHANNELS = tuple(f"E{i}" for i in range(1, 130))
CHANNEL_ALIASES = {"Cz": "E129"}
REQUIRED_EVENT_COLUMNS = ("onset", "trial_type", "sample", "trial", "item_name", "item_num")
LTPFR_TASK_LEVELS = (-1, 0, 1)  # events.json: -1 no task, 0 size, 1 animacy

# --- participant selection (Dataset Selection doc) ---------------------------
MIN_SESSIONS = 12
RECALL_RANGE = (0.15, 0.85)  # exclusive bounds on mean session recall
EEG_EXTENSION = ".edf"  # EGI recordings only in the first run
N_PILOT = 3
N_CONFIRMATORY = 20
PILOT_IDS = ("LTP063", "LTP065", "LTP066")
CONFIRMATORY_IDS = (
    "LTP067", "LTP069", "LTP070", "LTP073", "LTP077", "LTP079", "LTP081",
    "LTP082", "LTP084", "LTP085", "LTP086", "LTP087", "LTP088", "LTP089",
    "LTP090", "LTP091", "LTP092", "LTP093", "LTP094", "LTP095",
)

# --- EEG preprocessing and features -----------------------------------------
LINE_FREQ = 60.0  # eeg.json PowerLineFrequency
NOTCH_FREQS = (60.0, 120.0, 180.0)
HIGHPASS = 0.5
EPOCH_TMIN, EPOCH_TMAX = -1.0, 2.6  # seconds; buffer for wavelet edges
FEATURE_WINDOW = (0.2, 1.6)  # seconds after word onset
FREQS = np.geomspace(3.0, 128.0, 8)  # 3.0 5.1 8.8 15.0 25.6 43.8 74.9 128.0 Hz
N_CYCLES = np.clip(FREQS / 2.0, 3.0, None)
TFR_DECIM = 5
# Robustness model: low frequencies only, and no face/neck channels.
LOW_FREQ_MAX = 30.0
# Peripheral (face/neck/ear) channels are defined from the dataset's own
# *_electrodes.tsv: the lowest PERIPHERAL_FRACTION of EEG channels by z coordinate.
# The README warns these are generic cap positions, which is enough for this rule.
PERIPHERAL_FRACTION = 0.25
BAD_CHANNEL_Z = 5.0  # robust z of channel log-variance above which a channel is bad

# --- models -------------------------------------------------------------------
C_GRID = np.logspace(-4, 0, 5)
INNER_FOLDS = 5
RANDOM_SEED = 20261021
RECALLABILITY_PRIOR_WEIGHT = 5.0  # pseudo-observations shrinking item recall toward the mean

# --- statistics ---------------------------------------------------------------
SESOI_DELTA_AUC = 0.01
ALPHA = 0.05
N_BOOTSTRAP = 10_000
N_PERMUTATIONS = 200
HIGH_CONFIDENCE = 5  # recognition: "old" response with confidence 5 counts as a strong hit
