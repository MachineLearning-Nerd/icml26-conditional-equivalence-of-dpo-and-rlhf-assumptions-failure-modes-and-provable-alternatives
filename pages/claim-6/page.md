# Claim 6 — benchmark performance

**Final state: BLOCKED · confidence: LOW**

The narrower source statement is verified: CPO has the largest point estimate
in the paper's table (25.15 AlpacaEval WR, 26.57 LC, 32.6 Arena-Hard), and all
four claimed arithmetic differences recompute exactly. Independent benchmark
reproduction remains blocked after the mandatory routes:

1. **Source table:** PASS — The point estimates and arithmetic match the source table.
2. **Artifact provenance:** BLOCKED — A likely first-author 16.06 GB CPO checkpoint is frozen at an immutable Hub revision, but its card does not link the paper and contains no benchmark generations, judgments, dataset identity, or exact evaluator revisions.
3. **Official benchmark execution:** BLOCKED — The public benchmark code can score supplied answers, but the checkpoint still requires full-suite generation and the paper does not identify exact judge revisions. No saved outputs exist; GPU execution is outside campaign authorization.
4. **Falsification attempt:** INCONCLUSIVE — CPO and runner-up SimPO Arena-Hard intervals overlap, and no paired judgments or AlpacaEval intervals support a decisive significance test.

The CPO Arena-Hard 90% interval `[30.7,35.0]` overlaps SimPO's `[27.3,32.3]`.
No AlpacaEval intervals or paired judgments are supplied. The immutable 16.06
GB checkpoint makes model provenance materially stronger, but its model card
does not link the paper and supplies no benchmark outputs. Full-suite GPU
execution is outside campaign authorization, and the paper omits exact judge
revisions needed for a claim-faithful rerun.

- [Four-route raw audit](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/benchmark_audit_C6.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C6.json)

This is a durable blocker, not an estimate and not a hidden failure.
