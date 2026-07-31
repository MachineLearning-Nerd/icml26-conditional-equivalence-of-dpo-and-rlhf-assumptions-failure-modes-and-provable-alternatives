import json
from pathlib import Path


def interval(value, lower, upper):
    return value - lower, value + upper


def overlaps(left, right):
    return max(left[0], right[0]) <= min(left[1], right[1])


def run_benchmark_audit(contract_path):
    contract = json.loads(Path(contract_path).read_text())
    if contract["claim_id"] != "C6":
        raise ValueError("Claim contract mismatch")
    checkpoint_path = Path(contract_path).parents[1] / "c6_checkpoint_manifest.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    model = checkpoint["model"]
    artifacts = checkpoint["benchmark_artifacts"]
    if model["revision"] != "2d496b7103b3f17b033cac322b81270f5ec6cdac":
        raise AssertionError("C6 checkpoint revision changed")

    table = {
        "DPO": {"alpaca_wr": 24.60, "alpaca_lc": 25.09, "arena_wr": 28.9, "arena_ci": (1.7, 1.5)},
        "SimPO": {"alpaca_wr": 23.48, "alpaca_lc": 25.91, "arena_wr": 30.0, "arena_ci": (2.7, 2.3)},
        "CPO": {"alpaca_wr": 25.15, "alpaca_lc": 26.57, "arena_wr": 32.6, "arena_ci": (1.9, 2.4)},
    }
    cpo = table["CPO"]
    simpo = table["SimPO"]
    dpo = table["DPO"]
    cpo_interval = interval(cpo["arena_wr"], *cpo["arena_ci"])
    simpo_interval = interval(simpo["arena_wr"], *simpo["arena_ci"])

    route1 = {
        "name": "author_table_and_arithmetic",
        "passed": all(
            (
                cpo["alpaca_wr"] == max(row["alpaca_wr"] for row in table.values()),
                cpo["alpaca_lc"] == max(row["alpaca_lc"] for row in table.values()),
                cpo["arena_wr"] == max(row["arena_wr"] for row in table.values()),
                abs((cpo["alpaca_wr"] - dpo["alpaca_wr"]) - 0.55) < 1e-12,
                abs((cpo["alpaca_lc"] - simpo["alpaca_lc"]) - 0.66) < 1e-12,
                abs((cpo["arena_wr"] - simpo["arena_wr"]) - 2.6) < 1e-12,
                abs((cpo["arena_wr"] - dpo["arena_wr"]) - 3.7) < 1e-12,
            )
        ),
        "result": "The point estimates and arithmetic match the source table.",
    }
    route2 = {
        "name": "artifact_provenance",
        "passed": False,
        "checks": {
            "author_repository_available": False,
            "likely_first_author_cpo_checkpoint_available": True,
            "checkpoint_revision": model["revision"],
            "checkpoint_weight_bytes": model["weight_bytes"],
            "explicit_paper_link_in_model_card": checkpoint["provenance"]["explicit_paper_link_in_model_card"],
            "generation_outputs_available": bool(artifacts["generation_files"]),
            "pairwise_judgments_available": bool(artifacts["pairwise_judgments"]),
            "exact_training_configuration_available": False,
        },
        "result": "A likely first-author 16.06 GB CPO checkpoint is frozen at an immutable Hub revision, but its card does not link the paper and contains no benchmark generations, judgments, dataset identity, or exact evaluator revisions.",
    }
    route3 = {
        "name": "official_benchmark_execution",
        "passed": False,
        "checks": {
            "alpaca_eval_requires_model_outputs": True,
            "alpaca_eval_default_uses_api_judge": True,
            "arena_hard_requires_model_answers": True,
            "arena_hard_uses_api_judge": True,
            "required_cpo_model_available": True,
            "required_model_outputs_available": False,
            "exact_evaluator_revisions_available": False,
            "gpu_training_authorized": False,
        },
        "result": "The public benchmark code can score supplied answers, but the checkpoint still requires full-suite generation and the paper does not identify exact judge revisions. No saved outputs exist; GPU execution is outside campaign authorization.",
    }
    route4 = {
        "name": "falsification_with_reported_uncertainty",
        "passed": False,
        "checks": {
            "cpo_arena_90_ci": cpo_interval,
            "simpo_arena_90_ci": simpo_interval,
            "leading_arena_intervals_overlap": overlaps(cpo_interval, simpo_interval),
            "alpaca_confidence_intervals_reported": False,
            "paired_judgments_available": False,
        },
        "result": "CPO and runner-up SimPO Arena-Hard intervals overlap, and no paired judgments or AlpacaEval intervals support a decisive significance test.",
    }
    routes = [route1, route2, route3, route4]
    status = "BLOCKED"
    if not route1["passed"]:
        raise AssertionError("Author-report transcription check failed")
    if route2["passed"] or route3["passed"] or route4["passed"]:
        raise AssertionError("C6 status rule needs review; a blocking route unexpectedly passed")
    return {
        "claim_id": "C6",
        "status": status,
        "author_report_point_estimates": "VERIFIED",
        "independent_benchmark_reproduction": "BLOCKED",
        "table": table,
        "routes": routes,
        "checkpoint_manifest": checkpoint,
        "reason": "The paper's reported point ranking is transcribed correctly and a likely author checkpoint exists, but no generations, judgments, or exact evaluator revisions permit independent evaluation; the supplied uncertainty is not decisive.",
    }
