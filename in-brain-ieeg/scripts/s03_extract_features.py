"""Stage 3: iEEG features, one session at a time (label-blind).

For each session: download the bipolar EDF and sidecars, preprocess, compute log
Morlet power per word, save derivatives/features/sub-<ID>/ses-<N>.npz, then
delete the raw file unless --keep-raw is given. Already finished sessions are
skipped, so the script can be stopped and restarted.

Skip reasons (logged, session left out): the events file does not match the
expected structure (SchemaError, e.g. a word shown twice in one session or sample
and onset columns disagreeing), epochs too close to the file edge, sampling rate
too low for the highest analysis frequency, or the file cannot be read.

    python scripts/s03_extract_features.py R1066P [--sessions 0 1] [--keep-raw] [--jobs 4]
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
    eeg_key, ch_key = f"acq-{config.ACQ}_ieeg.edf", f"acq-{config.ACQ}_channels.tsv"
    log = []
    for ses, files in session_files(a.subject).items():
        if a.sessions is not None and ses not in a.sessions:
            continue
        out = out_dir / f"ses-{ses}.npz"
        if out.exists():
            print(f"ses-{ses}: done already")
            continue
        if not all(k in files for k in ("events.tsv", ch_key, eeg_key)):
            print(f"ses-{ses}: skipped (missing files)")
            log.append({"session": ses, "status": "skipped: missing files"})
            continue
        t0 = time.time()
        paths = {k: fetch(files[k]) for k in ("events.tsv", ch_key, eeg_key)}
        try:
            ev = load_events(paths["events.tsv"])
            words = study_table(ev)
            raw = preprocess(load_raw(paths[eeg_key], paths[ch_key]))
            X, chans = session_features(raw, words, ev, n_jobs=a.jobs)
        except (SchemaError, RuntimeError, ValueError, OSError) as err:
            print(f"ses-{ses}: skipped ({type(err).__name__}: {err})")
            log.append({"session": ses, "status": f"skipped: {type(err).__name__}: {err}"})
            if not a.keep_raw:
                paths[eeg_key].unlink(missing_ok=True)
            continue
        save_session(out, X, chans, words, raw.info["bads"])
        if not a.keep_raw:
            paths[eeg_key].unlink()
        dt = time.time() - t0
        log.append({"session": ses, "status": "ok", "n_words": len(words), "sfreq": raw.info["sfreq"],
                    "n_channels": len(chans), "bads": raw.info["bads"], "seconds": round(dt, 1)})
        print(f"ses-{ses}: {X.shape} features, {len(raw.info['bads'])} bad channels, {dt:.0f} s")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "extraction_log.jsonl", "a") as fh:
        for row in log:
            fh.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
