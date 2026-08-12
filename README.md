---
title: "ICML 2026 Reproduction — Conditional Equivalence of DPO and RLHF"
emoji: 🎯
colorFrom: yellow
colorTo: red
sdk: static
app_file: index.html
pinned: false
tags:
 - icml2026-repro
 - direct-preference-optimization
 - rlhf
 - cpo
 - reproducibility
---

# Conditional Equivalence of DPO and RLHF — ICML 2026 reproduction

This repository is an independent, evidence-first reproduction of:

> **Conditional Equivalence of DPO and RLHF: Implicit Assumption, Failure Modes, and Provable Alignment**
> Zhiqin Yang, Yonggang Zhang, Wei Xue, Dong Fang, Bo Han, and Yike Guo
> [arXiv:2605.20834](https://arxiv.org/abs/2605.20834)

Repository: [MachineLearning-Nerd/icml26-conditional-equivalence-of-dpo-and-rlhf-assumptions-failure-modes-and-provable-alternatives](https://github.com/MachineLearning-Nerd/icml26-conditional-equivalence-of-dpo-and-rlhf-assumptions-failure-modes-and-provable-alternatives)

The release does not treat every passing script as confirmation of the paper. Each claim has a contract, an executable checker, raw evidence, and a scoped verdict. The strongest current conclusion is:

| Claim | Result | How the result is produced |
| --- | --- | --- |
| C1 — conditional DPO/RLHF equivalence | **FALSIFIED** | `evidence/code/claim1_counterexample.py` proves all theorem premises and the strict boundary for a finite counterexample, then shows the printed DPO loss decreases away from the RLHF optimum. |
| C2 — relative objective under failure | **VERIFIED** | Exact objective identities and derivative checks in `evidence/code/formal_audit.py`, plus a predeclared nine-run real-preference pilot in `evidence/code/preference_pilot.py`. |
| C3 — undesirable solution region | **VERIFIED** | Exact witness and monotonicity checks, plus real-data trajectories that enter the declared region. |
| C4 — constrained-RLHF stationary loss | **VERIFIED** at the derivation scope | Direct differentiation, finite-difference control, omission controls, and the `gamma=0` DPO reduction pass; the scaled learned-policy improvement gate fails and is retained as negative evidence. |
| C5 — soft-margin ranking limit | **VERIFIED** | The uniform certificate `0 <= softplus(beta*a)/beta - max(0,a) <= log(2)/beta` is checked with boundary and reversed-argument controls. |
| C6 — benchmark performance | **BLOCKED** | The paper table and arithmetic are reproduced, but no generations, judgments, dataset identity, or exact evaluator revisions are available for an independent benchmark run. |

## Reproduction status and scope

The current release contains **4 VERIFIED, 1 FALSIFIED, and 1 BLOCKED** claims. “FALSIFIED” means the universal theorem fails under its printed ordered-pair objective; it does not claim that every DPO/RLHF relationship or every alternative population objective fails. “BLOCKED” means the available artifacts cannot support a claim-faithful test; it is not an estimate of the benchmark result.

The historical judged Space baseline is preserved, but is not the current verdict. Its immutable record is `DineshAI/7UEBX1KU1y` at revision `73b1ac8ff5dd201847e1e11cccc0ee0514beb728`; it received **5/12**, quality **low**, with five `toy` verdicts and one `inconclusive` verdict. The later release adds exact contracts, fail-closed checks, the real-preference pilot, and an explicit C6 blocker without deleting the historical pages.

## Repository map

- `pages/` — readable executive summary and one page for each claim; `index.html` is the static logbook entry point.
- `evidence/contracts/` — the predeclared scope and pass/fail obligations for C1–C6.
- `evidence/code/` — the counterexample, exact algebra audit, real-preference pilot, benchmark audit, release builder, and fail-closed verifier.
- `evidence/raw/` — machine-readable outputs used by the claim pages.
- `evidence/source_manifest.json` — source URLs, retrieval date, and hashes for the paper, benchmark repositories, and checkpoint metadata.
- `evidence/release_manifest.json` — SHA-256 hashes for the released evidence bundle.
- `branch-audit.md` — the purpose and evidence role of every retained branch after the cleanup.

## Reproduce the release

The pinned verification command is:

```bash
uv sync --frozen
uv run --frozen python -m reproduction.run
```

The recorded release used Python 3.12.11, NumPy 2.3.2, one CPU thread, seed `260520834`, and no GPU. The fail-closed release check is:

```bash
uv run --frozen python evidence/code/release_verifier.py
```

The scripts are deliberately scoped. They reproduce scalar theory, exact counterexamples, a small CPU preference pilot, and the benchmark evidence audit. They do not claim to retrain the paper’s 8B model or independently reproduce full AlpacaEval/Arena-Hard results without the missing model outputs and evaluator provenance.

## Citation

```bibtex
@article{yang2026conditional,
  title         = {Conditional Equivalence of DPO and RLHF: Implicit Assumption, Failure Modes, and Provable Alignment},
  author        = {Yang, Zhiqin and Zhang, Yonggang and Xue, Wei and Fang, Dong and Han, Bo and Guo, Yike},
  journal       = {arXiv preprint arXiv:2605.20834},
  year          = {2026},
  doi           = {10.48550/arXiv.2605.20834}
}
```

## Thank you

Thank you to Zhiqin Yang, Yonggang Zhang, Wei Xue, Dong Fang, Bo Han, and Yike Guo for making the paper’s assumptions, derivations, and experimental claims available for independent examination. This repository is an independent reproduction and audit; it is not an official implementation or an endorsement by the authors.

## Attribution

The cleanup documentation and approved repository-history normalization are maintained under the **MachineLearning-Nerd** GitHub identity. Historical evidence files retain their original timestamps, hashes, and external identifiers where changing them would invalidate the recorded artifact.
