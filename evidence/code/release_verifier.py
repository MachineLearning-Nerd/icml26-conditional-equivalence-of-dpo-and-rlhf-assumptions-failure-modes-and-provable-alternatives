import hashlib
import json
import re
import urllib.request


SPACE_ID = "DineshAI/7UEBX1KU1y"
JUDGED_REVISION = "73b1ac8ff5dd201847e1e11cccc0ee0514beb728"
EXPECTED_STATES = {
    "C1": "FALSIFIED",
    "C2": "VERIFIED",
    "C3": "VERIFIED",
    "C4": "VERIFIED",
    "C5": "VERIFIED",
    "C6": "BLOCKED",
}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ICMLPapers-release-verifier/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def verify_release_bundle(bundle, repo_root):
    logbook = json.loads((bundle / "logbook.json").read_text())
    claims = json.loads((bundle / "evidence/raw/claim_statuses.json").read_text())
    benchmark = json.loads((bundle / "evidence/raw/benchmark_audit_C6.json").read_text())
    pilot = json.loads((bundle / "evidence/raw/real_preference_pilot.json").read_text())
    judged_manifest = json.loads((repo_root / "evidence/judged_snapshot_manifest.json").read_text())
    current_space = fetch_json(f"https://huggingface.co/api/spaces/{SPACE_ID}")
    judged_tree = fetch_json(
        f"https://huggingface.co/api/spaces/{SPACE_ID}/tree/{JUDGED_REVISION}?recursive=true&expand=false"
    )
    judged_files = {item["path"] for item in judged_tree if item["type"] == "file"}
    old_nodes = {
        ("overview", "pages/overview/page.md"),
        ("claims", "pages/claims/page.md"),
        ("evidence", "pages/evidence/page.md"),
        ("conclusion", "pages/conclusion/page.md"),
        ("verification-run", "pages/verification-run/page.md"),
    }
    children = logbook["root"]["children"]
    current_nodes = {(node["slug"], node["file"]) for node in children}
    canonical_prefix = ["executive-summary", "claim-1", "claim-2", "claim-3", "claim-4", "claim-5", "claim-6", "current-conclusion"]
    page_text = "\n".join(path.read_text() for path in (bundle / "pages").rglob("*.md"))
    files = [path for path in bundle.rglob("*") if path.is_file()]
    manifest = json.loads((bundle / "evidence/release_manifest.json").read_text())
    manifest_valid = all(
        hashlib.sha256((bundle / path).read_bytes()).hexdigest() == digest
        for path, digest in manifest.items()
    )
    text_only = True
    secret_free = True
    for path in files:
        try:
            content = path.read_text()
        except UnicodeDecodeError:
            text_only = False
            continue
        secret_free &= re.search(r"(?:hf_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})", content) is None

    gates = {
        "01_expected_live_space_and_revision": current_space["id"] == SPACE_ID and current_space["sha"] == JUDGED_REVISION,
        "02_judged_file_manifest_matches_live_tree": set(judged_manifest["files"]) == judged_files,
        "03_all_historical_nodes_remain_reachable": old_nodes <= current_nodes,
        "04_canonical_current_page_order": [node["slug"] for node in children[:8]] == canonical_prefix,
        "05_final_states_are_exact_and_fail_closed": {item["id"]: item["status"] for item in claims} == EXPECTED_STATES,
        "06_every_claim_has_contract_and_page": all((bundle / f"evidence/contracts/C{number}.json").is_file() and (bundle / f"pages/claim-{number}/page.md").is_file() for number in range(1, 7)),
        "07_source_urls_and_archive_hashes_visible": "arxiv.org/e-print/2605.20834" in (bundle / "evidence/source_manifest.json").read_text(),
        "08_fixed_command_and_locked_environment": (bundle / "evidence/verification_command.txt").read_text().strip() == "uv sync --frozen && uv run --frozen python -m reproduction.run" and (bundle / "evidence/environment/uv.lock").is_file(),
        "09_raw_results_metadata_and_code_downloadable": all((bundle / f"evidence/raw/{name}").is_file() for name in ("claim1_counterexample.json", "formal_audit_C2_C5.json", "real_preference_pilot.json", "benchmark_audit_C6.json", "run_metadata.json")) and (bundle / "evidence/code/release_verifier.py").is_file(),
        "10_checker_controls_and_empirical_gate_visible": all(pilot["gates"][claim] for claim in ("C2", "C3")) and not pilot["gates"]["C4"] and "negative_controls" in (bundle / "evidence/raw/formal_audit_C2_C5.json").read_text(),
        "11_low_confidence_claim_has_four_routes_and_blocker": benchmark["status"] == "BLOCKED" and len(benchmark["routes"]) == 4 and "confidence: LOW" in page_text,
        "12_text_only_secret_free_hashed_bundle": text_only and secret_free and manifest_valid,
    }
    failed = [name for name, passed in gates.items() if not passed]
    if failed:
        raise AssertionError(f"Release gates failed: {failed}")
    return gates
