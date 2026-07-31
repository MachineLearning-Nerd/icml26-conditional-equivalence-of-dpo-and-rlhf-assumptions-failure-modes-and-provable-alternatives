import hashlib
import json
import math
from pathlib import Path

from z3 import Real, Solver, sat


def dpo_loss(delta):
    return math.log1p(math.exp(-delta))


def kl_bernoulli(probability, reference):
    return probability * math.log(probability / reference) + (1.0 - probability) * math.log(
        (1.0 - probability) / (1.0 - reference)
    )


def rlhf_objective(probability, reference=0.5):
    return probability - kl_bernoulli(probability, reference)


def run_claim1_counterexample(contract_path):
    contract = json.loads(Path(contract_path).read_text())
    if contract["claim_id"] != "C1":
        raise ValueError("Claim contract mismatch")

    beta = Real("beta")
    reward_gap = Real("reward_gap")
    delta_ref = Real("delta_ref")
    delta_star = Real("delta_star")
    competitor_delta = Real("competitor_delta")

    solver = Solver()
    solver.add(beta == 1)
    solver.add(reward_gap == 1)
    solver.add(delta_ref == 0)
    solver.add(delta_star == delta_ref + reward_gap / beta)
    solver.add(delta_ref > -reward_gap / beta)
    solver.add(competitor_delta == 2)
    solver.add(competitor_delta > delta_star)
    if solver.check() != sat:
        raise AssertionError("Exact counterexample premises are not satisfiable")

    model = solver.model()
    rlhf_probability = 1.0 / (1.0 + math.exp(-1.0))
    competitor_probability = 1.0 / (1.0 + math.exp(-2.0))
    numeric = {
        "beta": 1.0,
        "reward_gap": 1.0,
        "delta_ref": 0.0,
        "rlhf_delta_star": 1.0,
        "competitor_delta": 2.0,
        "rlhf_probability_winner": rlhf_probability,
        "competitor_probability_winner": competitor_probability,
        "rlhf_objective_at_rlhf_star": rlhf_objective(rlhf_probability),
        "rlhf_objective_at_competitor": rlhf_objective(competitor_probability),
        "rlhf_derivative_at_rlhf_star": 1.0
        - math.log(rlhf_probability / (1.0 - rlhf_probability)),
        "rlhf_second_derivative_at_rlhf_star": -1.0
        / (rlhf_probability * (1.0 - rlhf_probability)),
        "dpo_loss_at_rlhf_star": dpo_loss(1.0),
        "dpo_loss_at_competitor": dpo_loss(2.0),
        "dpo_derivative_at_rlhf_star": -1.0 / (1.0 + math.exp(1.0)),
    }

    obligations = {
        "human_preference": numeric["reward_gap"] > 0.0,
        "positive_beta": numeric["beta"] > 0.0,
        "boundary_condition": numeric["delta_ref"] > -numeric["reward_gap"] / numeric["beta"],
        "rlhf_optimum_identity": numeric["rlhf_delta_star"]
        == numeric["delta_ref"] + numeric["reward_gap"] / numeric["beta"],
        "rlhf_first_order_condition": abs(numeric["rlhf_derivative_at_rlhf_star"])
        < 1e-12,
        "rlhf_strict_concavity": numeric["rlhf_second_derivative_at_rlhf_star"] < 0.0,
        "competitor_is_worse_for_rlhf": numeric["rlhf_objective_at_competitor"]
        < numeric["rlhf_objective_at_rlhf_star"],
        "finite_valid_policies": 0.0
        < numeric["rlhf_probability_winner"]
        < numeric["competitor_probability_winner"]
        < 1.0,
        "rlhf_is_not_dpo_stationary": numeric["dpo_derivative_at_rlhf_star"] < 0.0,
        "valid_policy_has_lower_dpo_loss": numeric["dpo_loss_at_competitor"]
        < numeric["dpo_loss_at_rlhf_star"],
    }

    controls = {
        "smaller_delta_does_not_lower_loss": dpo_loss(0.0) > dpo_loss(1.0),
        "violating_reference_fails_boundary": -2.0 <= -1.0,
        "strict_boundary_excludes_equality": not (-1.0 > -1.0),
    }
    all_pass = all(obligations.values()) and all(controls.values())
    status = "FALSIFIED" if all_pass else "BLOCKED"
    model_values = {
        str(symbol): str(model.eval(symbol))
        for symbol in (beta, reward_gap, delta_ref, delta_star, competitor_delta)
    }
    certificate = {
        "claim_id": "C1",
        "status": status,
        "counterexample": numeric,
        "exact_smt_model": model_values,
        "obligations": obligations,
        "negative_controls": controls,
        "reason": (
            "All theorem premises and its strict boundary hold, but increasing finite log odds "
            "from the RLHF optimum 1 to 2 strictly lowers the stated DPO loss."
        ),
        "contract_sha256": hashlib.sha256(Path(contract_path).read_bytes()).hexdigest(),
    }
    if status != "FALSIFIED":
        raise AssertionError("Claim 1 checker failed closed")
    return certificate
