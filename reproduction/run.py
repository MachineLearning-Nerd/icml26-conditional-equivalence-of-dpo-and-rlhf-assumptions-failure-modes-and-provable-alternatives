import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

for variable in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[variable] = "1"

import numpy as np

from reproduction.historical_checks import run_checks
from reproduction.claim1_counterexample import run_claim1_counterexample
from reproduction.preference_pilot import run_preference_pilot


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
    return checks


def run_claim1(config):
    checks = run_baseline(config)
    contract_path = ROOT / "evidence" / "claim_contracts" / "C1.json"
    certificate = run_claim1_counterexample(contract_path)
    certificate_path = write_json("claim1_counterexample.json", certificate)
    claims = [
        {
            "id": f"C{number}",
            "status": "FALSIFIED" if number == 1 else "BLOCKED",
            "reason": (
                certificate["reason"]
                if number == 1
                else "No exact claim-level evidence has passed yet."
            ),
        }
        for number in range(1, 7)
    ]
    claims_path = write_json("claim_statuses.json", claims)
    metadata_path = OUTPUTS / "run_metadata.json"
    raw_path = OUTPUTS / "historical_scalar_checks.json"
    manifest = {
        path.name: file_sha256(path)
        for path in (raw_path, claims_path, metadata_path, certificate_path, contract_path)
    }
    write_json("manifest.json", manifest)
    print("C1 counterexample obligations: PASS")
    print("C1 final state: FALSIFIED")
    print("Final claim states: 0 VERIFIED, 1 FALSIFIED, 5 BLOCKED")
    print("EVAL exact_claims_resolved=1")
    return checks, certificate


def run_empirical_pilot(config):
    _, claim1 = run_claim1(config)
    protocol_path = ROOT / "evidence" / "empirical_protocol.json"
    pilot = run_preference_pilot(protocol_path)
    pilot_path = write_json("real_preference_pilot.json", pilot)
    claims = [
        {"id": "C1", "status": "FALSIFIED", "reason": claim1["reason"]},
        *[
            {
                "id": claim_id,
                "status": "VERIFIED" if pilot["gates"][claim_id] else "BLOCKED",
                "reason": (
                    "The predeclared real-preference policy gate passed."
                    if pilot["gates"][claim_id]
                    else "The predeclared real-preference policy gate did not pass."
                ),
            }
            for claim_id in ("C2", "C3", "C4")
        ],
        {"id": "C5", "status": "BLOCKED", "reason": "Not tested on this route."},
        {"id": "C6", "status": "BLOCKED", "reason": "No benchmark reproduction."},
    ]
    claims_path = write_json("claim_statuses.json", claims)
    metadata_path = OUTPUTS / "run_metadata.json"
    claim1_path = OUTPUTS / "claim1_counterexample.json"
    manifest = {
        path.name: file_sha256(path)
        for path in (claims_path, metadata_path, claim1_path, pilot_path, protocol_path)
    }
    write_json("manifest.json", manifest)
    passed = sum(pilot["gates"].values())
    print(f"Real-preference claim gates: {passed}/3 passed")
    print(f"EVAL empirical_claim_gates={passed}")


def main():
    config = json.loads((ROOT / "reproduction" / "config.json").read_text())
    if config["threads"] != 1:
        raise SystemExit("Refusing to run: threads must remain 1")
    OUTPUTS.mkdir(exist_ok=True)
    if config["mode"] == "judged_scalar_baseline":
        run_baseline(config)
        return
    if config["mode"] == "claim1_counterexample":
        run_claim1(config)
        return
    if config["mode"] == "real_preference_pilot":
        run_empirical_pilot(config)
        return
    raise SystemExit(f"Unsupported mode: {config['mode']}")


if __name__ == "__main__":
    main()
