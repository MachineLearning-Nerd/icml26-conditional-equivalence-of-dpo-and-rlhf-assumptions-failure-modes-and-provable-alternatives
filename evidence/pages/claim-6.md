# Claim 6 — benchmark performance

**Final state: BLOCKED.** The author-reported point estimates are internally
verified, but the benchmark result is not independently reproducible.

## Route 1 — source table

The exact arXiv source table gives CPO the largest reported point estimate on
all three metrics: AlpacaEval WR 25.15, AlpacaEval LC 26.57, and Arena-Hard WR
32.6. The stated improvements (+0.55 over DPO WR, +0.66 over SimPO LC, +2.6
over SimPO Arena-Hard, and +3.7 over DPO Arena-Hard) recompute exactly.

## Route 2 — artifacts

The paper-linked `https://github.com/visitworld123/CPO` returned “repository
not found” on 2026-07-31. A likely first-author CPO checkpoint was located at
the immutable Hugging Face revision
`2d496b7103b3f17b033cac322b81270f5ec6cdac`. Its four BF16 weight shards total
16.06 GB, but the model card does not link the paper and contains no benchmark
generations, pair-level judgments, dataset identity, or exact evaluator revisions.

## Route 3 — official benchmark pipelines

The official AlpacaEval and Arena-Hard repositories can score supplied model
outputs using API judges. Searches at revisions `cd543a149df89434d8a54582c0151c0b945c3d20`
and `196f6b826783b3da7310e361a805fa36f0be83f3` found no matching generations or
scores. The checkpoint permits generation in principle, but full-suite GPU
execution is outside this campaign's authorization and the paper does not name
the exact judge revisions required for a claim-faithful rerun.

## Route 4 — falsification attempt

The reported Arena-Hard 90% intervals are CPO `[30.7, 35.0]` and SimPO
`[27.3, 32.3]`; they overlap. The paper supplies no AlpacaEval intervals and no
paired judgments for a direct significance test. This neither falsifies the
point-estimate ranking nor independently establishes a reliable improvement.

The executable audit in `reproduction/benchmark_audit.py` recomputes every
number and enforces the `BLOCKED` rule. It keeps the narrower source statement
“the paper reports the top point estimates in its table” separate from the
unverified claim that those benchmark results reproduce.
