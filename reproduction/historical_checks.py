import math


def sigmoid(value):
    return 1.0 / (1.0 + math.exp(-value))


def loss(delta, delta_ref, beta, margin=0.0):
    value = beta * (delta - delta_ref) - margin
    return math.log1p(math.exp(-value))


def descend(delta_ref, beta, margin=0.0, steps=6000, rate=0.05):
    delta = delta_ref + 0.1
    for _ in range(steps):
        value = beta * (delta - delta_ref) - margin
        gradient = -beta * sigmoid(-value)
        delta -= rate * gradient
    return delta


def run_checks():
    beta = 1.0
    reward_gap = 2.0
    boundary = -reward_gap / beta

    equivalence_cases = []
    equivalence_ok = True
    for delta_ref in (2.0, 0.0, boundary + 0.5, boundary - 0.5, -3.0):
        delta_star = delta_ref + reward_gap / beta
        equivalent = delta_ref > boundary
        equivalence_ok &= equivalent == (delta_star > 0.0)
        equivalence_cases.append(
            {"delta_ref": delta_ref, "delta_star": delta_star, "equivalent": equivalent}
        )

    delta_ref = -3.0
    rlhf_star = delta_ref + reward_gap / beta
    dpo_final = descend(delta_ref, beta)
    shift = 0.7
    shift_invariant = abs(loss(1.0, 0.5, beta) - loss(1.0 + shift, 0.5 + shift, beta)) < 1e-12

    undesirable_delta_ref = -2.0
    gradient_factors = [
        sigmoid(-beta * (delta - undesirable_delta_ref))
        for delta in (-1.5, -1.0, -0.5, 0.0)
    ]

    cpo_margin = -beta * delta_ref
    cpo_target = delta_ref + cpo_margin / beta
    cpo_final = descend(delta_ref, beta, cpo_margin)

    checks = [
        {
            "id": "historical-C1",
            "passed": equivalence_ok,
            "detail": {"boundary": boundary, "cases": equivalence_cases},
        },
        {
            "id": "historical-C2",
            "passed": rlhf_star < 0.0 and dpo_final > 1.0 and shift_invariant,
            "detail": {
                "delta_ref": delta_ref,
                "rlhf_delta_star": rlhf_star,
                "dpo_final_delta": dpo_final,
                "loss_shift_invariant": shift_invariant,
            },
        },
        {
            "id": "historical-C3",
            "passed": all(
                left > right for left, right in zip(gradient_factors, gradient_factors[1:])
            ),
            "detail": {"delta_ref": undesirable_delta_ref, "gradient_factors": gradient_factors},
        },
        {
            "id": "historical-C4",
            "passed": cpo_target >= 0.0 and cpo_final > 0.0,
            "detail": {
                "delta_ref": delta_ref,
                "margin": cpo_margin,
                "effective_target": cpo_target,
                "final_delta": cpo_final,
            },
        },
        {
            "id": "historical-C5",
            "passed": beta * -3.0 < 0.0 and beta * 0.5 > 0.0,
            "detail": {"negative_target": beta * -3.0, "positive_target": beta * 0.5},
        },
    ]
    return checks
