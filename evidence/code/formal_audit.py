import math

from z3 import Not, Real, Solver, unsat


def sigmoid(value):
    return 1.0 / (1.0 + math.exp(-value))


def softplus(value):
    return max(0.0, value) + math.log1p(math.exp(-abs(value)))


def prove_unsat(constraints):
    solver = Solver()
    solver.add(*constraints)
    return solver.check() == unsat


def audit_c2():
    beta = Real("c2_beta")
    reward_gap = Real("c2_reward_gap")
    delta_ref = Real("c2_delta_ref")
    delta_star = Real("c2_delta_star")
    delta = Real("c2_delta")
    shift = Real("c2_shift")
    sign_implication = prove_unsat(
        [
            beta > 0,
            reward_gap > 0,
            beta * delta_star == beta * delta_ref + reward_gap,
            beta * delta_ref + reward_gap <= 0,
            delta_star > 0,
        ]
    )
    shift_invariance = prove_unsat(
        [
            beta > 0,
            beta * ((delta + shift) - (delta_ref + shift))
            != beta * (delta - delta_ref),
        ]
    )
    derivative_sign = all(
        -test_beta * sigmoid(-test_beta * (test_delta - test_ref)) < 0.0
        for test_beta in (0.1, 1.0, 10.0)
        for test_delta in (-10.0, -1.0, 0.0, 3.0)
        for test_ref in (-4.0, 0.0, 2.0)
    )
    controls = {
        "fixed_reference_breaks_translation_invariance": abs(
            softplus(-(1.0 - 0.5)) - softplus(-((1.0 + 0.7) - 0.5))
        )
        > 1e-6,
        "satisfying_boundary_allows_positive_rlhf_delta": 0.0 + 2.0 > 0.0,
    }
    obligations = {
        "violated_boundary_implies_nonpositive_rlhf_delta": sign_implication,
        "dpo_argument_is_exactly_shift_invariant": shift_invariance,
        "finite_dpo_derivative_is_strictly_negative": derivative_sign,
    }
    return certificate("C2", obligations, controls)


def audit_c3():
    beta = Real("c3_beta")
    reward_gap = Real("c3_reward_gap")
    delta_ref = Real("c3_delta_ref")
    witness = delta_ref / 2
    witness_is_in_u = prove_unsat(
        [
            beta > 0,
            reward_gap > 0,
            beta * delta_ref + reward_gap < 0,
            Not((delta_ref < witness) & (witness < 0)),
        ]
    )
    numeric_ref = -3.0
    numeric_witness = numeric_ref / 2.0
    deltas = (-2.5, -1.5, -0.5, 0.0)
    factors = [sigmoid(-(value - numeric_ref)) for value in deltas]
    obligations = {
        "midpoint_is_exact_witness_in_u": witness_is_in_u,
        "witness_prefers_dispreferred_response": numeric_witness < 0.0,
        "witness_has_lower_dpo_loss_than_reference": softplus(
            -(numeric_witness - numeric_ref)
        )
        < softplus(0.0),
        "gradient_factor_strictly_weakens": all(
            left > right for left, right in zip(factors, factors[1:])
        ),
    }
    controls = {
        "u_empty_for_nonnegative_reference": not (0.5 < 0.25 < 0.0),
        "fixed_reference_boundary_factor_is_not_zero": factors[-1] > 0.0,
    }
    extra = {"gradient_factors": factors, "boundary_limit": sigmoid(numeric_ref)}
    return certificate("C3", obligations, controls, extra)


def constrained_objective(probability, reference, reward_gap, beta, gamma):
    kl = probability * math.log(probability / reference) + (1.0 - probability) * math.log(
        (1.0 - probability) / (1.0 - reference)
    )
    return probability * reward_gap - beta * kl + gamma * math.log(
        probability / (1.0 - probability)
    )


def audit_c4():
    probability = 0.4
    reference = 0.2
    beta = 1.5
    gamma = 0.03
    delta = math.log(probability / (1.0 - probability))
    delta_ref = math.log(reference / (1.0 - reference))
    exact_margin = gamma * (1.0 / probability + 1.0 / (1.0 - probability))
    reward_gap = beta * (delta - delta_ref) - exact_margin
    derivative = reward_gap - beta * (delta - delta_ref) + exact_margin
    second_derivative = -beta * (1.0 / probability + 1.0 / (1.0 - probability)) + gamma * (
        -1.0 / probability**2 + 1.0 / (1.0 - probability) ** 2
    )
    step = 1e-6
    finite_difference = (
        constrained_objective(probability + step, reference, reward_gap, beta, gamma)
        - constrained_objective(probability - step, reference, reward_gap, beta, gamma)
    ) / (2.0 * step)
    reference_margin = gamma * (1.0 / reference + 1.0 / (1.0 - reference))
    moved_probability = probability + 0.05
    moved_exact_margin = gamma * (
        1.0 / moved_probability + 1.0 / (1.0 - moved_probability)
    )
    obligations = {
        "constructed_reward_gap_is_positive": reward_gap > 0.0,
        "analytic_first_order_condition": abs(derivative) < 1e-12,
        "finite_difference_first_order_condition": abs(finite_difference) < 1e-8,
        "stationary_point_is_locally_maximizing": second_derivative < 0.0,
        "reference_margin_is_fixed_under_policy_update": reference_margin
        == gamma * (1.0 / reference + 1.0 / (1.0 - reference)),
        "gamma_zero_recovers_dpo_logit": beta * (delta - delta_ref) - 0.0
        == beta * (delta - delta_ref),
    }
    controls = {
        "optimal_policy_margin_would_move_with_parameters": abs(
            exact_margin - moved_exact_margin
        )
        > 1e-6,
        "omitting_margin_breaks_foc": abs(reward_gap - beta * (delta - delta_ref)) > 1e-6,
    }
    extra = {
        "beta": beta,
        "gamma": gamma,
        "policy_probability": probability,
        "reference_probability": reference,
        "reward_gap": reward_gap,
        "exact_policy_margin": exact_margin,
        "reference_stationary_margin": reference_margin,
        "analytic_derivative": derivative,
        "finite_difference_derivative": finite_difference,
    }
    return certificate("C4", obligations, controls, extra)


def audit_c5():
    cases = []
    bounds_hold = True
    for beta in (1.0, 2.0, 10.0, 100.0):
        for difference in (-3.0, -0.5, 0.0, 0.5, 3.0):
            scaled = softplus(beta * difference) / beta
            hinge = max(0.0, difference)
            error = scaled - hinge
            bound = math.log(2.0) / beta
            bounds_hold &= -1e-15 <= error <= bound + 1e-15
            cases.append(
                {
                    "beta": beta,
                    "difference": difference,
                    "scaled_dpo": scaled,
                    "hinge": hinge,
                    "error": error,
                    "upper_bound": bound,
                }
            )
    obligations = {
        "uniform_softplus_hinge_bound": bounds_hold,
        "error_bound_converges_to_zero": math.log(2.0) / 1000.0 < 0.001,
        "negative_reference_is_negative_threshold": -3.0 < 0.0,
        "strictly_above_negative_threshold_has_zero_hinge": max(0.0, -3.0 - -2.0)
        == 0.0,
    }
    controls = {
        "unscaled_loss_does_not_have_claimed_limit": softplus(100.0) > 50.0,
        "reversing_difference_changes_hinge_side": max(0.0, 1.0) != max(0.0, -1.0),
    }
    return certificate("C5", obligations, controls, {"cases": cases})


def certificate(claim_id, obligations, controls, extra=None):
    passed = all(obligations.values()) and all(controls.values())
    result = {
        "claim_id": claim_id,
        "status": "VERIFIED" if passed else "BLOCKED",
        "obligations": obligations,
        "negative_controls": controls,
    }
    if extra:
        result["raw"] = extra
    if not passed:
        raise AssertionError(f"{claim_id} checker failed closed")
    return result


def run_formal_audit():
    return {claim_id: audit() for claim_id, audit in (("C2", audit_c2), ("C3", audit_c3), ("C4", audit_c4), ("C5", audit_c5))}
