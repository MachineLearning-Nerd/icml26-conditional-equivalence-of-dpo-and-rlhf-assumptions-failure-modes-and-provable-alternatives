# Claim 2 — relative objective under failure

**Final state: VERIFIED · confidence: HIGH**

For all `beta>0`, positive reward gaps, and finite references satisfying
`delta_ref <= -reward_gap/beta`, exact-real arithmetic proves the RLHF identity
has `delta_star<=0`. The DPO argument is invariant to an arbitrary common shift
of policy and reference log odds, and its derivative is strictly negative at
every finite delta. This verifies optimization of relative advantage and the
objective-level distinction.

The real-data route trained nine paired policies (3 seeds × 3 corrupted
references) on 384 train and 128 held-out pairs. Its predeclared C2 gate passed:
all DPO runs lowered the objective and at least one learned reference was
misaligned on held-out pairs.

- [Formal raw certificate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/formal_audit_C2_C5.json)
- [Real-data raw runs](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/real_preference_pilot.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C2.json)

Limitation: unconstrained DPO eventually pushes a scalar delta upward; this
claim distinguishes objectives and does not assert permanent misalignment.
