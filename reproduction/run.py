import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

import numpy as np

from reproduction.historical_checks import run_checks


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def write_json(name, value):
    path = OUTPUTS / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return path


def git_sha():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_baseline(config):
    started = time.monotonic()
    checks = run_checks()
    passed = sum(check["passed"] for check in checks)
    claims = [
        {
            "id": f"C{number}",
            "status": "BLOCKED",
            "reason": "The frozen judge awarded only a toy/scalar partial pass; exact evidence is absent.",
        }
        for number in range(1, 7)
    ]
    raw_path = write_json("historical_scalar_checks.json", checks)
    claims_path = write_json("claim_statuses.json", claims)
    metadata = {
        "arxiv": "2605.20834",
        "command": "uv sync --frozen && uv run --frozen python -m reproduction.run",
        "config": config,
        "cpu_count_visible": os.cpu_count(),
        "git_sha": git_sha(),
        "judged_space_revision": "73b1ac8ff5dd201847e1e11cccc0ee0514beb728",
        "numpy": np.__version__,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "runtime_seconds": time.monotonic() - started,
        "seed": config["seed"],
        "threads_used": config["threads"],
    }
    metadata_path = write_json("run_metadata.json", metadata)
    manifest = {
        path.name: file_sha256(path) for path in (raw_path, claims_path, metadata_path)
    }
    write_json("manifest.json", manifest)
    print(f"Historical scalar checks: {passed}/{len(checks)} passed")
    print("Final claim states: 0 VERIFIED, 0 FALSIFIED, 6 BLOCKED")
    print(f"EVAL historical_scalar_checks={passed}")


def main():
    config = json.loads((ROOT / "reproduction" / "config.json").read_text())
    if config["threads"] != 1:
        raise SystemExit("Refusing to run: threads must remain 1")
    if config["mode"] != "judged_scalar_baseline":
        raise SystemExit(f"Unsupported mode: {config['mode']}")
    OUTPUTS.mkdir(exist_ok=True)
    run_baseline(config)


if __name__ == "__main__":
    main()
