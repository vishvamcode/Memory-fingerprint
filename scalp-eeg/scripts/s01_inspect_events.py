"""Stage 1: inspect the structure of every session of some participants. No EEG download.

Downloads events.tsv/json, channels.tsv and eeg.json, then prints and saves a
report per session: columns, event types, list structure, recall rate,
recognition coverage, channel counts and sampling rate. Run this first and read
the output before trusting any later stage.

    python scripts/s01_inspect_events.py LTP063 LTP065 LTP066
"""
import json
import sys

import pandas as pd

from pnms import config
from pnms.download import fetch, session_files
from pnms.events import load_events, schema_report

SIDECARS = ("events.tsv", "events.json", "channels.tsv", "eeg.json")


def main(subjects):
    out_dir = config.DERIV_DIR / "inspection"
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in subjects:
        sessions = session_files(sub)
        print(f"\n=== sub-{sub}: {len(sessions)} {config.TASK} sessions")
        reports = {}
        for ses, files in sessions.items():
            missing = [s for s in SIDECARS if s not in files]
            if missing:
                print(f"  ses-{ses}: MISSING {missing}")
                continue
            paths = {s: fetch(files[s]) for s in SIDECARS}
            ev = load_events(paths["events.tsv"])
            rep = schema_report(ev)
            eeg_json = json.loads(paths["eeg.json"].read_text())
            ch = pd.read_csv(paths["channels.tsv"], sep="\t")
            rep["sfreq"] = eeg_json.get("SamplingFrequency")
            rep["reference"] = eeg_json.get("EEGReference")
            rep["cap"] = eeg_json.get("CapManufacturersModelName")
            rep["channel_types"] = ch["type"].value_counts().to_dict()
            rep["eeg_file"] = next((k for k in files if k.startswith("eeg.")), None)
            rep["eeg_file_mb"] = round(files[rep["eeg_file"]].size / 1e6, 1) if rep["eeg_file"] else None
            if rep["sfreq"]:
                err = (ev.loc[ev.trial_type == config.STUDY_EVENT, "onset"] * rep["sfreq"]
                       - ev.loc[ev.trial_type == config.STUDY_EVENT, "sample"]).abs().max()
                rep["sample_matches_onset"] = bool(err <= 1.0)
            reports[ses] = rep
            print(f"  ses-{ses:>2}: {rep['n_study_words']} words in {rep['n_lists']} lists "
                  f"(sizes {rep['words_per_list']}), recall {rep['recall_rate']:.2f}, "
                  f"recog-tested {rep['n_recog_tested']}, task {rep.get('task_counts')}, "
                  f"{rep['sfreq']} Hz, {rep['eeg_file']} {rep['eeg_file_mb']} MB, "
                  f"sample ok: {rep['sample_matches_onset']}")
        (out_dir / f"sub-{sub}_inspection.json").write_text(json.dumps(reports, indent=1, default=str))
    print(f"\nReports written to {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1:] or list(config.PILOT_IDS))
