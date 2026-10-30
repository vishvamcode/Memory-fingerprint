"""Stage 3: EEG features, one session at a time (label-blind).

For each session: download the EEG file and sidecars, preprocess, compute log
Morlet power per word (EEG channels, and separately the 4 EOG channels
for the ocular control model), save derivatives/features/sub-<ID>/ses-<N>.npz, then
delete the raw EEG file unless --keep-raw is given. Already finished sessions
are skipped, so the script can be stopped and restarted.

    python scripts/s03_extract_features.py LTP063 [--sessions 0 1] [--keep-raw] [--jobs 4]
"""
import argparse
import json
import time

from pnms import config
from pnms.download import fetch, session_files
from pnms.eeg_features import load_raw, preprocess, save_session, session_features
from pnms.events import SchemaError, load_events, study_table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--sessions", type=int, nargs="*")
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()

    out_dir = config.DERIV_DIR / "features" / f"sub-{a.subject}"
    log = []
    for ses, files in session_files(a.subject).items():
        if a.sessions is not None and ses not in a.sessions:
            continue
        out = out_dir / f"ses-{ses}.npz"
        if out.exists():
            print(f"ses-{ses}: done already")
            continue
        eeg_key = next((k for k in files if k.startswith("eeg.") and not k.endswith(".json")), None)
        if eeg_key is None or not eeg_key.endswith(config.EEG_EXTENSION):
            print(f"ses-{ses}: skipped (EEG file {eeg_key})")
            log.append({"session": ses, "status": f"skipped: {eeg_key}"})
            continue
        t0 = time.time()
        paths = {k: fetch(files[k]) for k in ("events.tsv", "channels.tsv", "electrodes.tsv", eeg_key)}
        ev = load_events(paths["events.tsv"])
        words = study_table(ev)
        raw = preprocess(load_raw(paths[eeg_key], paths["channels.tsv"]))
        try:
            X, chans = session_features(raw, words, ev, n_jobs=a.jobs)
            X_eog, _ = session_features(raw, words, ev, n_jobs=a.jobs, ch_type="eog")
        except (SchemaError, RuntimeError) as err:  # pre-registered skip reasons: timing mismatch, epochs at file edge
            print(f"ses-{ses}: skipped ({err})")
            log.append({"session": ses, "status": f"skipped: {err}"})
            continue
        save_session(out, X, chans, words, raw.info["bads"], X_eog=X_eog)
        if not a.keep_raw:
            paths[eeg_key].unlink()
        dt = time.time() - t0
        log.append({"session": ses, "status": "ok", "n_words": len(words), "bads": raw.info["bads"], "seconds": round(dt, 1)})
        print(f"ses-{ses}: {X.shape} features, {len(raw.info['bads'])} bad channels, {dt:.0f} s")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "extraction_log.jsonl", "a") as fh:
        for row in log:
            fh.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
