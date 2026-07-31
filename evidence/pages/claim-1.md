# Claim 1 — conditional equivalence

**Final state: FALSIFIED.**

## Exact contract

The theorem quantifies over every ordered preference triple with reward gap
`r*(y_w)-r*(y_l)>0` and every `beta>0`. It says DPO and KL-regularized RLHF
have equivalent objectives exactly when every pair obeys
`delta_ref > -reward_gap/beta`. The executable contract is
`evidence/claim_contracts/C1.json`.

Source: arXiv:2605.20834 source archive, `main/implicit_assu.tex`, theorem
`thm:conditional_equivalence`, and `appendix/proof.tex`, section `app:ce`.

## Exact counterexample

Use one prompt and two responses, `beta=1`, a uniform reference
(`delta_ref=0`), and rewards `(1, 0)`. The strict condition holds because
`0 > -1`. KL-regularized RLHF has the finite optimum `delta_star=1`.

For the paper's ordered-pair DPO loss,

```text
L(delta) = -log sigmoid(delta)
dL/ddelta = -sigmoid(-delta) < 0
```

Thus `delta_star=1` is not stationary. The valid finite competitor `delta=2`
has strictly lower loss. This single instance refutes the theorem's universal
sufficiency direction.

The appendix itself states that this DPO loss is monotonically decreasing and
pushes `delta` to infinity, but later calls the finite RLHF policy a stationary
global DPO optimum. The executable checker tests the former formula directly.

## Reproduce and controls

```bash
uv sync --frozen && uv run --frozen python -m reproduction.run
```

The checker requires all premises, a satisfiable exact-real SMT model, a
nonzero derivative, and a lower-loss finite competitor. It also checks three
negative controls: a smaller log-odds perturbation, a reference outside the
boundary, and equality at the strict boundary. Any failed obligation changes
the result to `BLOCKED` and exits nonzero.

## Scope

This falsifies the exact ordered-pair objective printed in the theorem and
proof. A population cross-entropy that explicitly averages both stochastic
labels for the same pair is a different objective and is not rejected here.
