#!/usr/bin/env python3
"""Verify the published DPO/RLHF audit surface, branches, and claim boundary."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOSITORY = "MachineLearning-Nerd/icml26-conditional-equivalence-of-dpo-and-rlhf-assumptions-failure-modes-and-provable-alternatives"
EXPECTED_URL = f"https://github.com/{REPOSITORY}"
EXPECTED_IDENTITY = "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"
OVERALL = "PARTIAL_CLAIMS_C1_FALSIFIED_C2_TO_C5_VERIFIED_SCOPED_C6_BENCHMARK_BLOCKED"
BOUNDARY = "C1_PRINTED_ORDERED_PAIR_COUNTEREXAMPLE_C4_SCALED_LEARNED_POLICY_GATE_FAILED_C6_MISSING_GENERATIONS_JUDGMENTS_EVALUATOR_REVISIONS"
EXPECTED_BRANCHES = {
    "main",
    "audit/c6-author-checkpoint-provenance",
    "audit/claim-1-proof-obligations",
    "audit/exact-algebra-c2-c5",
    "audit/judged-scalar-baseline",
    "audit/release-bundle-gate",
    "experiment/cpo-margin-strength-0-2",
    "experiment/real-preference-policy-pilot",
    "release/combined-candidate",
}
CLAIM_STATUSES = {
    "C1": "falsified_printed_ordered_pair_equivalence",
    "C2": "verified_scoped_exact_objective_and_pilot",
    "C3": "verified_scoped_undesirable_region",
    "C4": "verified_scoped_derivation_comparative_gate_failed",
    "C5": "verified_scoped_uniform_certificate",
    "C6": "blocked_missing_benchmark_provenance",
}
SOURCE_SHA256 = {
    "https://ar5iv.labs.arxiv.org/html/2605.20834": "80809c80491058f7c041b4c7668560e6d06703c9218f8466368e5b05170d1c8e",
    "https://arxiv.org/e-print/2605.20834": "cec74f481515079f9124c63b4c88d31528712518358d5c5735025ae044eea841",
}


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def fail(message: str) -> None:
    print(f"FINAL_AUDIT=FAILED reason={message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> dict | list:
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid_json_{path.replace('/', '_')}_{type(exc).__name__}")
        raise AssertionError


def remote_branch_map() -> dict[str, str]:
    output = git("ls-remote", "--heads", "origin")
    return {
        line.split("\t", 1)[1].removeprefix("refs/heads/"): line.split("\t", 1)[0]
        for line in output.splitlines()
        if line.strip()
    }


def ref_for_branch(branch: str) -> str:
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        result = subprocess.run(["git", "show-ref", "--verify", "--quiet", ref], cwd=ROOT)
        if result.returncode == 0:
            return ref
    fail(f"missing_branch_ref_{branch.replace('/', '_')}")
    raise AssertionError


def main() -> None:
    remote_map = remote_branch_map()
    if set(remote_map) != EXPECTED_BRANCHES:
        fail(f"remote_branches_expected_9_observed_{len(remote_map)}")
    local = set(git("for-each-ref", "--format=%(refname:strip=2)", "refs/heads").splitlines())
    if local - EXPECTED_BRANCHES or "main" not in local:
        fail("local_branch_refs_are_not_a_subset_with_main")
    for branch, remote_sha in remote_map.items():
        if git("rev-parse", ref_for_branch(branch)) != remote_sha:
            fail(f"remote_tip_mismatch_{branch.replace('/', '_')}")
    if "refs/heads/main\tHEAD" not in git("ls-remote", "--symref", "origin", "HEAD"):
        fail("remote_default_branch_is_not_main")
    if git("remote", "get-url", "origin").removesuffix(".git") != EXPECTED_URL:
        fail("origin_url_mismatch")
    if git("status", "--porcelain"):
        fail("working_tree_not_clean")
    if git("for-each-ref", "--format=%(refname)", "refs/original"):
        fail("rewrite_backup_refs_present")

    identities = set(git("log", "--all", "--format=%an <%ae> | %cn <%ce>").splitlines())
    if identities != {EXPECTED_IDENTITY + " | " + EXPECTED_IDENTITY}:
        fail("non_canonical_commit_identity_present")
    if "Co-authored-by:" in git("log", "--all", "--format=%B"):
        fail("coauthor_trailer_present")
    commit_count = int(git("rev-list", "--all", "--count"))

    required = [
        "README.md",
        "branch-audit.md",
        "CLAIM_EVIDENCE.md",
        "SOURCE_AUDIT.md",
        "ENVIRONMENT.md",
        "REPORT.md",
        "CITATION.cff",
        "AUTHOR_THANK_YOU.md",
        "STATUS.md",
        "claims.json",
        "reproduction_verdicts.json",
        "AUTONOMOUS_STATE.json",
        "EVIDENCE_MANIFEST.json",
        "verify_final.py",
        "evidence/contracts/C1.json",
        "evidence/contracts/C6.json",
        "evidence/raw/claim_statuses.json",
        "evidence/raw/benchmark_audit_C6.json",
        "evidence/judged_verdict.json",
        "evidence/source_manifest.json",
        "evidence/release_manifest.json",
    ]
    for path in required:
        if not (ROOT / path).is_file():
            fail(f"missing_required_file_{path.replace('/', '_')}")

    state = load_json("AUTONOMOUS_STATE.json")
    assert isinstance(state, dict)
    if state["repository"] != REPOSITORY or state["branch_layout"]["expected_count"] != 9:
        fail("autonomous_state_repository_or_branch_count_mismatch")
    if set(state["branch_layout"]["branches"]) != EXPECTED_BRANCHES:
        fail("autonomous_state_branch_list_mismatch")
    if state["audit"]["overall_verdict"] != OVERALL or state["audit"]["publication_boundary"] != BOUNDARY:
        fail("autonomous_state_boundary_mismatch")
    if state["audit"]["publication_allowed"] or state["audit"]["score_claim"] or state["audit"]["official_author_endorsement"]:
        fail("autonomous_state_publication_flags_must_be_false")
    if state["history"]["expected_reachable_commits"] != commit_count:
        fail("autonomous_state_commit_count_mismatch")
    if state["history"]["published_main_parent"] != git("rev-parse", "main^"):
        fail("autonomous_state_main_parent_mismatch")
    if state["attribution"]["canonical_identity"] != EXPECTED_IDENTITY:
        fail("autonomous_state_attribution_mismatch")

    claims = load_json("claims.json")
    assert isinstance(claims, dict)
    if claims["overall_verdict"] != OVERALL or claims["publication_boundary"] != BOUNDARY:
        fail("machine_readable_claim_boundary_mismatch")
    if claims["publication_allowed"] or claims["score_claim"] or claims["official_author_endorsement"]:
        fail("machine_readable_publication_flags_must_be_false")
    if {item["id"]: item["status"] for item in claims["claims"]} != CLAIM_STATUSES:
        fail("machine_readable_claim_status_mismatch")

    verdicts = load_json("reproduction_verdicts.json")
    assert isinstance(verdicts, dict)
    if verdicts["overall_verdict"] != OVERALL or verdicts["publication_boundary"] != BOUNDARY:
        fail("machine_readable_verdict_boundary_mismatch")
    if {key: value["status"] for key, value in verdicts["claims"].items()} != CLAIM_STATUSES:
        fail("machine_readable_verdict_status_mismatch")
    historical = verdicts["historical_judge"]
    if historical["points"] != 5 or historical["total"] != 12 or not historical["current_score_not_claimed"]:
        fail("historical_score_boundary_mismatch")

    raw_statuses = load_json("evidence/raw/claim_statuses.json")
    if {item["id"]: item["status"] for item in raw_statuses} != {
        "C1": "FALSIFIED",
        "C2": "VERIFIED",
        "C3": "VERIFIED",
        "C4": "VERIFIED",
        "C5": "VERIFIED",
        "C6": "BLOCKED",
    }:
        fail("raw_claim_status_mismatch")
    judged = load_json("evidence/judged_verdict.json")
    if judged["score"] != 5 or judged["score_total"] != 12:
        fail("judged_snapshot_score_mismatch")
    source_manifest = load_json("evidence/source_manifest.json")
    sources = {item["url"]: item.get("sha256") for item in source_manifest["sources"]}
    for url, expected_sha in SOURCE_SHA256.items():
        if sources.get(url) != expected_sha:
            fail("source_manifest_hash_mismatch")

    manifest = load_json("EVIDENCE_MANIFEST.json")
    if manifest["repository"] != REPOSITORY or manifest["overall_verdict"] != OVERALL:
        fail("evidence_manifest_header_mismatch")
    branch_audit = (ROOT / "branch-audit.md").read_text(encoding="utf-8")
    if any(branch not in branch_audit for branch in EXPECTED_BRANCHES):
        fail("branch_audit_mapping_incomplete")

    print(
        "FINAL_AUDIT=VERIFIED "
        f"branches={len(remote_map)} commits={commit_count} "
        "claims=C1:falsified_printed_ordered_pair_equivalence,C2:verified_scoped_exact_objective_and_pilot,"
        "C3:verified_scoped_undesirable_region,C4:verified_scoped_derivation_comparative_gate_failed,"
        "C5:verified_scoped_uniform_certificate,C6:blocked_missing_benchmark_provenance "
        "historical_score=5/12 current_score_claim=false publication_allowed=false"
    )


if __name__ == "__main__":
    main()
