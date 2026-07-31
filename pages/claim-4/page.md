# Claim 4 — constrained-RLHF stationary loss

**Final state: VERIFIED · confidence: MEDIUM**

Direct differentiation of the two-response constrained-RLHF objective recovers
the paper's inverse-probability adaptive margin. The analytic first-order
residual is 0.0; a central finite
difference gives 2.776e-11.
Omitting the margin breaks the condition, replacing optimal-policy
probabilities with reference probabilities makes it stationary, and `gamma=0`
recovers DPO.

The scaled learned-policy comparison is retained as negative evidence: at
`gamma=0.02`, mean DPO/CPO held-out accuracy was
0.5321/0.5304, and
mean escape rate was 0.3158/0.3193.
The predeclared empirical C4 improvement gate therefore failed. This does not
contradict the narrower derivation contract.

- [Formal certificate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/formal_audit_C2_C5.json)
- [Failed empirical gate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/real_preference_pilot.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C4.json)

Limitation: no global convergence or absolute-advantage theorem is claimed by
this reproduction state.
