# Claim 1 — conditional equivalence

**Final state: FALSIFIED · confidence: HIGH**

## Exact claim and quantifiers

For every ordered preference triple with reward gap `>0` and every `beta>0`,
the paper claims DPO and KL-regularized RLHF optimize equivalent objectives iff
`delta_ref > -reward_gap/beta` for every pair. The contract assumes positive
finite response probabilities, the paper's RLHF identity
`delta_star=delta_ref+reward_gap/beta`, and its printed ordered-pair DPO loss.

Source: arXiv:2605.20834 source archive, `main/implicit_assu.tex`, theorem
`thm:conditional_equivalence`, and `appendix/proof.tex`, section `app:ce`.

## Counterexample

| beta | reward gap | delta_ref | RLHF delta* | competitor delta |
| ---: | ---: | ---: | ---: | ---: |
| 1.0 | 1.0 | 0.0 | 1.0 | 2.0 |

The strict boundary holds. RLHF's objective is 0.620115
at delta 1 versus 0.552984 at delta 2. The DPO
loss moves the other way: 0.313262 to
0.126928, with derivative
-0.268941 at the RLHF optimum. Hence that optimum
is not even stationary for the stated DPO objective.

Independent routes in one certificate: exact SMT premises, direct RLHF
first/second-order checks, a finite lower-loss DPO competitor, and three
mutation controls. Any failure returns `BLOCKED` and exits nonzero.

- [Raw certificate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/claim1_counterexample.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C1.json)
- [Executable checker](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/code/claim1_counterexample.py)

## Limitation

This falsifies the ordered-pair objective printed in the theorem. A different
population cross-entropy that explicitly averages both stochastic labels for
the same pair is outside this contract.
