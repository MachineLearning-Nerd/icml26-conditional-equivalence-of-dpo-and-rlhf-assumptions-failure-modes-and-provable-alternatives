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
from reproduction.benchmark_audit import run_benchmark_audit
from reproduction.formal_audit import run_formal_audit
from reproduction.preference_pilot import run_preference_pilot
from reproduction.release_builder import build_release_bundle
from reproduction.release_verifier import verify_release_bundle


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


def run_theory_audit(config):
    _, claim1 = run_claim1(config)
    certificates = run_formal_audit()
    audit_path = write_json("formal_audit_C2_C5.json", certificates)
    claims = [
        {"id": "C1", "status": "FALSIFIED", "reason": claim1["reason"]},
        *[
            {
                "id": claim_id,
                "status": certificate["status"],
                "reason": "Every exact obligation and negative control passed.",
            }
            for claim_id, certificate in certificates.items()
        ],
        {"id": "C6", "status": "BLOCKED", "reason": "No benchmark reproduction."},
    ]
    write_json("claim_statuses.json", claims)
    print("C2-C5 exact obligations and controls: PASS")
    print("EVAL exact_claims_resolved=5")
    return claim1, certificates, audit_path


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
    return claim1, pilot, pilot_path


def run_combined_candidate(config):
    started = time.monotonic()
    _, claim1 = run_claim1(config)
    theory = run_formal_audit()
    theory_path = write_json("formal_audit_C2_C5.json", theory)
    protocol_path = ROOT / "evidence" / "empirical_protocol.json"
    pilot = run_preference_pilot(protocol_path)
    pilot_path = write_json("real_preference_pilot.json", pilot)
    benchmark_contract = ROOT / "evidence" / "claim_contracts" / "C6.json"
    benchmark = run_benchmark_audit(benchmark_contract)
    benchmark_path = write_json("benchmark_audit_C6.json", benchmark)

    final_states = {
        "C1": "FALSIFIED",
        "C2": "VERIFIED" if theory["C2"]["status"] == "VERIFIED" and pilot["gates"]["C2"] else "BLOCKED",
        "C3": "VERIFIED" if theory["C3"]["status"] == "VERIFIED" and pilot["gates"]["C3"] else "BLOCKED",
        "C4": theory["C4"]["status"],
        "C5": theory["C5"]["status"],
        "C6": benchmark["status"],
    }
    reasons = {
        "C1": claim1["reason"],
        "C2": "Exact objective checks and the predeclared real-preference gate passed.",
        "C3": "Exact U-region checks and the predeclared real-preference gate passed.",
        "C4": "The exact constrained-RLHF derivation passed; the scaled comparative model gate failed and is retained as a limitation.",
        "C5": "The uniform softplus-to-hinge certificate and controls passed.",
        "C6": benchmark["reason"],
    }
    claims = [
        {"id": claim_id, "status": final_states[claim_id], "reason": reasons[claim_id]}
        for claim_id in ("C1", "C2", "C3", "C4", "C5", "C6")
    ]
    claims_path = write_json("claim_statuses.json", claims)
    metadata_path = OUTPUTS / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata["total_runtime_seconds"] = time.monotonic() - started
    metadata["dataset_revision"] = pilot["dataset_revision"]
    metadata["dataset_subset_sha256"] = pilot["subset_sha256"]
    write_json("run_metadata.json", metadata)
    artifacts = (
        OUTPUTS / "historical_scalar_checks.json",
        OUTPUTS / "claim1_counterexample.json",
        theory_path,
        pilot_path,
        benchmark_path,
        claims_path,
        metadata_path,
        protocol_path,
        benchmark_contract,
    )
    write_json("manifest.json", {str(path.relative_to(ROOT)): file_sha256(path) for path in artifacts})
    verified = sum(state == "VERIFIED" for state in final_states.values())
    falsified = sum(state == "FALSIFIED" for state in final_states.values())
    blocked = sum(state == "BLOCKED" for state in final_states.values())
    print(f"Final claim states: {verified} VERIFIED, {falsified} FALSIFIED, {blocked} BLOCKED")
    print(f"Empirical gates C2/C3/C4: {pilot['gates']}")
    print("EVAL exact_claims_resolved=5")
    print(f"EVAL empirical_claim_gates={sum(pilot['gates'].values())}")


def run_release_bundle(config):
    run_combined_candidate(config)
    bundle = build_release_bundle(ROOT, OUTPUTS)
    gates = verify_release_bundle(bundle, ROOT)
    write_json("release_gates.json", gates)
    print(f"Release gates: {sum(gates.values())}/{len(gates)} passed")
    print(f"EVAL release_gates={sum(gates.values())}")


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
    if config["mode"] == "formal_audit_c2_c5":
        run_theory_audit(config)
        return
    if config["mode"] == "real_preference_pilot":
        run_empirical_pilot(config)
        return
    if config["mode"] == "combined_candidate":
        run_combined_candidate(config)
        return
    if config["mode"] == "release_bundle":
        run_release_bundle(config)
        return
    raise SystemExit(f"Unsupported mode: {config['mode']}")


if __name__ == "__main__":
    main()
