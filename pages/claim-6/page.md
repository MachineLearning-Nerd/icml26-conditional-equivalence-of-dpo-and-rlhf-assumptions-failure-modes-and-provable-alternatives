# Claim 6 — benchmark performance

**Final state: BLOCKED · confidence: LOW**

The narrower source statement is verified: CPO has the largest point estimate
in the paper's table (25.15 AlpacaEval WR, 26.57 LC, 32.6 Arena-Hard), and all
four claimed arithmetic differences recompute exactly. Independent benchmark
reproduction remains blocked after the mandatory routes:

1. **Source table:** PASS — The point estimates and arithmetic match the source table.
2. **Artifact provenance:** BLOCKED — The paper-linked GitHub repository returned repository not found; no immutable model or generations were located.
3. **Official benchmark execution:** BLOCKED — The public benchmark code is executable, but the missing CPO checkpoint/generations cannot be regenerated under the no-GPU rule.
4. **Falsification attempt:** INCONCLUSIVE — CPO and runner-up SimPO Arena-Hard intervals overlap, and no paired judgments or AlpacaEval intervals support a decisive significance test.

The CPO Arena-Hard 90% interval `[30.7,35.0]` overlaps SimPO's `[27.3,32.3]`.
No AlpacaEval intervals or paired judgments are supplied. GPU training is not
authorized, and the missing Llama-3-8B checkpoint/generations cannot be
recreated through the CPU route.

- [Four-route raw audit](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/benchmark_audit_C6.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C6.json)

This is a durable blocker, not an estimate and not a hidden failure.
