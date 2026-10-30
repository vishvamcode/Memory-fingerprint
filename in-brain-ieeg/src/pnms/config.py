"""Fixed analysis settings.

Everything a reviewer could suspect of being tuned on the test data lives here.
Change values only before the pre-registration is posted; after that, any change
must be reported together with the original result.
"""
import os
from pathlib import Path

import numpy as np

# --- dataset -----------------------------------------------------------------
# Sub-project 1: the same test on intracranial recordings (RAM delayed free recall).
DATASET_ID = "ds004789"
DATASET_VERSION = "3.1.0"  # dataset_description.json DatasetDOI: doi:10.18112/openneuro.ds004789.v3.1.0
S3_ROOT = f"https://s3.amazonaws.com/openneuro.org/{DATASET_ID}"
TASK = "FR1"
ACQ = "bipolar"  # README: monopolar files must be re-referenced; bipolar ones are ready to use

# Local folders. Override with the PNMS_DATA / PNMS_DERIV environment variables.
DATA_DIR = Path(os.environ.get("PNMS_DATA", "data")).resolve()
DERIV_DIR = Path(os.environ.get("PNMS_DERIV", "derivatives")).resolve()

# --- event schema (verified on the real files, 21 Oct 2026) -------------------
STUDY_EVENT = "WORD"
RECALL_EVENT = "REC_WORD"
RECOG_TARGET_EVENT = "RECOG_TARGET"
# RAM events (verified on sub-R1001P ses-0, 23 Oct 2026): columns onset, sample,
# trial_type, item_name, serialpos, list, stim_file, ...; no item number and no
# "recalled" column. Practice words are PRACTICE_WORD (list -1). Every session shows
# the same 300 words of its word pool (25 lists x 12), so a session hold-out alone
# cannot keep test words out of training; see WORD_FOLDS.
RAM_REQUIRED_EVENT_COLUMNS = ("onset", "sample", "trial_type", "item_name", "list", "stim_file")
# The `sample` column, not `onset`, is aligned with the iEEG file: onset is offset by
# the session start and drifts (up to 0.2 s in sub-R1001P ses-0), and word-locked
# evoked responses are larger when epochs use `sample`.
MAX_ONSET_SAMPLE_DRIFT_S = 1.0
# EGI HydroCel 129 layout (PEERS only; unused for iEEG). Features are stored in this fixed order in every session,
# because which channels are EOG (E25 or E26) and how the EDF names channels
# ("E1" or "EEG E1"; reference "E129" or "Cz") differ between sessions (seen in
# sub-LTP063 ses-1, ses-5, ses-8 and sub-LTP065 ses-7).
EGI_CHANNELS = tuple(f"E{i}" for i in range(1, 130))
CHANNEL_ALIASES = {"Cz": "E129"}
REQUIRED_EVENT_COLUMNS = ("onset", "trial_type", "sample", "trial", "item_name", "item_num")
LTPFR_TASK_LEVELS = (-1, 0, 1)  # events.json: -1 no task, 0 size, 1 animacy

# --- participant selection ------------------------------------------------------
# Eligible: >= MIN_SESSIONS FR1 sessions that each have a bipolar EDF and an events
# file, mean recall inside RECALL_RANGE. Eligible IDs are shuffled with
# SELECTION_SEED; the first N_PILOT are the pilot, the next N_CONFIRMATORY the test.
MIN_SESSIONS = 3
SELECTION_SEED = 20261023
RECALL_RANGE = (0.15, 0.85)  # exclusive bounds on mean session recall
EEG_EXTENSION = ".edf"  # EGI recordings only in the first run
N_PILOT = 3
N_CONFIRMATORY = 20
PILOT_IDS = ("R1066P", "R1168T", "R1108J")  # s00 output, 23 Oct 2026
RESERVE_IDS = ("R1067P", "R1092J", "R1309M", "R1147P", "R1195E")  # next in the shuffled order
CONFIRMATORY_IDS = (
    "R1077T", "R1068J", "R1311T", "R1123C", "R1151E", "R1334T", "R1111M",
    "R1292E", "R1377M", "R1145J", "R1222M", "R1121M", "R1158T", "R1350D",
    "R1217T", "R1243T", "R1345D", "R1060M", "R1125T", "R1391T",
)

# --- EEG preprocessing and features -----------------------------------------
LINE_FREQ = 60.0  # ieeg.json PowerLineFrequency (US sites)
NOTCH_FREQS = (60.0, 120.0, 180.0)
HIGHPASS = 0.5
EPOCH_TMIN, EPOCH_TMAX = -1.0, 2.6  # seconds; buffer for wavelet edges
FEATURE_WINDOW = (0.2, 1.6)  # seconds after word onset
FREQS = np.geomspace(3.0, 128.0, 8)  # 3.0 5.1 8.8 15.0 25.6 43.8 74.9 128.0 Hz
N_CYCLES = np.clip(FREQS / 2.0, 3.0, None)
TFR_DECIM = 5
# Robustness model: low frequencies only (iEEG has no face/neck channels to drop).
LOW_FREQ_MAX = 30.0
# Peripheral (face/neck/ear) channels are defined from the dataset's own
# *_electrodes.tsv: the lowest PERIPHERAL_FRACTION of EEG channels by z coordinate.
# The README warns these are generic cap positions, which is enough for this rule.
PERIPHERAL_FRACTION = 0.25
BAD_CHANNEL_Z = 5.0  # robust z of channel log-variance above which a channel is bad

# --- models -------------------------------------------------------------------
C_GRID = np.logspace(-4, 0, 5)
INNER_FOLDS = 5
# Words are split into WORD_FOLDS fixed groups (by word, seeded). Outer test set =
# one session x one word group; training = other sessions AND other word groups.
# Inner folds use the same rule. This keeps every test word out of training even
# though all sessions share the same words.
WORD_FOLDS = 4
MIN_INNER_TEST = 20  # smallest inner test fold (words); added after the iEEG pilot
RANDOM_SEED = 20261021
RECALLABILITY_PRIOR_WEIGHT = 5.0  # pseudo-observations shrinking item recall toward the mean

# --- statistics ---------------------------------------------------------------
SESOI_DELTA_AUC = 0.01
ALPHA = 0.05
N_BOOTSTRAP = 10_000
N_PERMUTATIONS = 200
HIGH_CONFIDENCE = 5  # recognition: "old" response with confidence 5 counts as a strong hit
