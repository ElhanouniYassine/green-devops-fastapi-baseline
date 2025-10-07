#!/usr/bin/env python3
import argparse, subprocess, sys, json
from datetime import datetime
from pathlib import Path
from codecarbon import EmissionsTracker

def run_and_track(cmd, label, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    tracker = EmissionsTracker(
        output_dir=str(outdir),
        output_file=f"emissions_{label}.csv",
        measure_power_secs=1,
        save_to_file=True,
        log_level="warning",
    )
    tracker.start()
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        code = result.returncode
    finally:
        emissions = tracker.stop()
    summary = {
        "label": label,
        "cmd": cmd,
        "returncode": code,
        "emissions_kg": emissions,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    (outdir / f"summary_{label}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))  # For CI logs/step-summary
    return code

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--label", required=True)
    p.add_argument("--outdir", default="metrics-optimized")
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    args = p.parse_args()
    if not args.cmd:
        print("No command provided.", file=sys.stderr)
        sys.exit(2)
    sys.exit(run_and_track(" ".join(args.cmd), args.label, args.outdir))

if __name__ == "__main__":
    main()
