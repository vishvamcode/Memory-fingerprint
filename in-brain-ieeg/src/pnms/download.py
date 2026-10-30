"""List and download RAM FR1 files from the public OpenNeuro S3 bucket.

No account is needed: the bucket answers plain HTTPS requests. Paths follow
the BIDS layout verified on the real dataset:

    ds004789/sub-<ID>/ses-<N>/ieeg/sub-<ID>_ses-<N>_task-FR1_<suffix>
"""
from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from . import config

BUCKET_URL = "https://s3.amazonaws.com/openneuro.org"


@dataclass(frozen=True)
class RemoteFile:
    key: str  # e.g. "ds004395/sub-LTP063/ses-0/eeg/sub-LTP063_ses-0_task-ltpFR_events.tsv"
    size: int

    @property
    def url(self) -> str:
        return f"{BUCKET_URL}/{self.key}"

    @property
    def relpath(self) -> str:
        """Path inside the dataset, without the dataset id."""
        return self.key.split("/", 1)[1]


def list_files(prefix: str) -> list[RemoteFile]:
    """List every object under `prefix` (e.g. 'ds004395/sub-LTP063/')."""
    out, token = [], None
    while True:
        query = {"list-type": "2", "prefix": prefix}
        if token:
            query["continuation-token"] = token
        url = f"{BUCKET_URL}?{urllib.parse.urlencode(query)}"
        xml = _get(url).decode()
        for key, size in re.findall(r"<Key>(.*?)</Key>.*?<Size>(\d+)</Size>", xml, re.S):
            out.append(RemoteFile(key, int(size)))
        m = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", xml)
        if not m:
            return out
        token = m.group(1)


def session_files(subject: str, task: str = config.TASK) -> dict[int, dict[str, RemoteFile]]:
    """Map session number -> {suffix: RemoteFile} for one participant's iEEG folder.

    Suffixes look like "events.tsv", "acq-bipolar_ieeg.edf", "acq-bipolar_channels.tsv".
    """
    pattern = re.compile(
        rf"{config.DATASET_ID}/sub-{subject}/ses-(\d+)/ieeg/sub-{subject}_ses-\1_task-{task}_([\w-]+\.\w+)$"
    )
    sessions: dict[int, dict[str, RemoteFile]] = {}
    for f in list_files(f"{config.DATASET_ID}/sub-{subject}/"):
        m = pattern.match(f.key)
        if m:
            sessions.setdefault(int(m.group(1)), {})[m.group(2)] = f
    return dict(sorted(sessions.items()))


def fetch(remote: RemoteFile, root: Path = config.DATA_DIR, retries: int = 4) -> Path:
    """Download one file unless a complete copy already exists. Verifies size."""
    dest = root / remote.relpath
    if dest.exists() and dest.stat().st_size == remote.size:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(remote.url, timeout=120) as r, open(tmp, "wb") as fh:
                while chunk := r.read(1 << 20):
                    fh.write(chunk)
            if tmp.stat().st_size != remote.size:
                raise OSError(f"size mismatch for {remote.key}: {tmp.stat().st_size} != {remote.size}")
            tmp.replace(dest)
            return dest
        except OSError:
            if attempt == retries:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")


def _get(url: str, retries: int = 4) -> bytes:
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except OSError:
            if attempt == retries:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")
