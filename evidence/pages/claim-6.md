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
not found” on 2026-07-31. No CPO checkpoint, immutable generations, exact
training configuration, or pair-level benchmark judgments were located.

## Route 3 — official benchmark pipelines

The official AlpacaEval and Arena-Hard repositories can score supplied model
outputs using API judges. They cannot recreate absent CPO outputs. Training the
paper's Llama-3-8B setup would require GPU compute, which is explicitly outside
this campaign's authorization.

## Route 4 — falsification attempt

The reported Arena-Hard 90% intervals are CPO `[30.7, 35.0]` and SimPO
`[27.3, 32.3]`; they overlap. The paper supplies no AlpacaEval intervals and no
paired judgments for a direct significance test. This neither falsifies the
point-estimate ranking nor independently establishes a reliable improvement.

The executable audit in `reproduction/benchmark_audit.py` recomputes every
number and enforces the `BLOCKED` rule. It keeps the narrower source statement
“the paper reports the top point estimates in its table” separate from the
unverified claim that those benchmark results reproduce.
