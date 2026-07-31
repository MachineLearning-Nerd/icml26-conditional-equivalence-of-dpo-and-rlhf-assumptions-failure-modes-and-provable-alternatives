# Claims 2–5 — exact algebra audit

**Final states: C2 VERIFIED · C3 VERIFIED · C4 VERIFIED · C5 VERIFIED.**

All checks use the fixed command and the exact contracts in
`evidence/claim_contracts`. Raw machine-readable certificates are written to
`outputs/formal_audit_C2_C5.json`; any failed obligation or negative control
exits nonzero and changes the affected claim to `BLOCKED`.

## C2 — relative rather than absolute objective

When `beta>0` and `beta*delta_ref+reward_gap<=0`, exact-real arithmetic proves
the RLHF identity implies `delta_star<=0`. The DPO logit is unchanged by adding
the same arbitrary shift to `delta` and `delta_ref`, and its finite derivative
is always negative. This verifies that the printed DPO objective depends on
relative advantage and differs from the finite RLHF optimum. It does not claim
that unconstrained DPO remains negative forever.

## C3 — undesirable solution region

Under `delta_ref < -reward_gap/beta`, `delta_ref/2` is an exact witness in
`U={delta_ref<delta<0}`. It still prefers the rejected response, but strict DPO
monotonicity gives it lower loss than the reference. The gradient factor
strictly weakens toward zero. For a fixed finite reference its boundary limit
is positive, `sigmoid(beta*delta_ref)`, so this audit does not endorse a literal
zero-gradient claim.

## C4 — stationary adaptive margin

Direct differentiation of the two-response constrained-RLHF objective gives
the paper's inverse-probability margin. A central finite difference confirms
the constructed first-order point, omitting the margin breaks it, and replacing
the optimal-policy probabilities with reference probabilities makes the margin
constant under policy updates. Setting `gamma=0` recovers the DPO logit. This
checks the derivation, not the paper's separate convergence guarantees.

## C5 — soft-margin limit

Writing `a=delta_ref-delta`, the checker uses the uniform certificate

```text
0 <= softplus(beta*a)/beta - max(0,a) <= log(2)/beta.
```

The bound proves the pointwise limit for every fixed finite pair and includes
the equality boundary, both signs, four temperatures, and controls for the
required normalization and argument direction. The hinge threshold is
`delta_ref`, which is negative whenever the reference log odds are negative.
