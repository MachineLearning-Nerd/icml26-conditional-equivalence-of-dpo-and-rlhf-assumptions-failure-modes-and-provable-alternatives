# Claim 3 — undesirable solution region

**Final state: VERIFIED · confidence: HIGH**

With `delta_ref < -reward_gap/beta`, the exact witness `delta_ref/2` lies in
`U={delta_ref<delta<0}`: it still prefers the rejected response but has lower
DPO loss than the reference. Exact monotonicity and boundary controls pass.

On the real paper dataset, all nine DPO trajectories lowered loss and at least
one entered U, satisfying the predeclared C3 gate. The observed maximum U
fractions ranged from 0.198
to 0.495.

- [Formal raw certificate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/formal_audit_C2_C5.json)
- [Real-data trajectories](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/real_preference_pilot.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C3.json)

Limitation: for fixed finite `delta_ref`, the gradient factor's limit at the
zero boundary is positive, not literally zero. The release verifies weakening,
not an exact zero-gradient statement.
