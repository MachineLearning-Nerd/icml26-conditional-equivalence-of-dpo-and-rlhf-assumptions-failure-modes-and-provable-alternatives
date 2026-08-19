# Source audit

## Paper identity

The audited paper is *Conditional Equivalence of DPO and RLHF: Implicit
Assumption, Failure Modes, and Provable Alignment*, by Zhiqin Yang, Yonggang
Zhang, Wei Xue, Dong Fang, Bo Han, and Yike Guo.

- [arXiv:2605.20834](https://arxiv.org/abs/2605.20834)
- [OpenReview 7UEBX1KU1y](https://openreview.net/forum?id=7UEBX1KU1y)
- Current repository: [MachineLearning-Nerd/icml26-conditional-equivalence-of-dpo-and-rlhf-assumptions-failure-modes-and-provable-alternatives](https://github.com/MachineLearning-Nerd/icml26-conditional-equivalence-of-dpo-and-rlhf-assumptions-failure-modes-and-provable-alternatives)

This is an independent reproduction and audit, not the authors' implementation
and not an author endorsement.

## Retrieved sources

| Source | Use | Recorded SHA-256 or status |
| --- | --- | --- |
| [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2605.20834) | Exact claims and section context | `80809c80491058f7c041b4c7668560e6d06703c9218f8466368e5b05170d1c8e` |
| [arXiv source archive](https://arxiv.org/e-print/2605.20834) | `implicit_assu.tex` and theorem wording omitted by HTML | `cec74f481515079f9124c63b4c88d31528712518358d5c5735025ae044eea841` |
| Author-linked [CPO repository](https://github.com/visitworld123/CPO) | Implementation provenance | unavailable at retrieval time (HTTP repository not found) |
| [Likely first-author checkpoint](https://huggingface.co/visity/llama-3-instruct-8b-cpo-full-beta-2.5_alpha-0.25_e-version-false-lr-1e-6/tree/2d496b7103b3f17b033cac322b81270f5ec6cdac) | Immutable model metadata | revision `2d496b7103b3f17b033cac322b81270f5ec6cdac`; no benchmark generations in model card |

The full source URL and hash record is preserved in
[`evidence/source_manifest.json`](evidence/source_manifest.json).

## Boundary

C1's finite counterexample is a direct disproof of the printed universal
claim under its stated ordered-pair objective. C2–C5 are scoped exact-algebra,
finite-control, and small-pilot checks. C6 remains blocked because checkpoint
metadata is not equivalent to generations, judgments, dataset identity, or
evaluator revisions.
