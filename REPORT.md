# Audit report

## Decision

The correct public status is:

```text
PARTIAL_CLAIMS_C1_FALSIFIED_C2_TO_C5_VERIFIED_SCOPED_C6_BENCHMARK_BLOCKED
```

C1 is falsified under the paper's printed ordered-pair DPO objective by a
finite counterexample that satisfies the theorem premises. C2–C5 pass their
registered scoped contracts, while C6 is blocked by missing benchmark
provenance. The historical judged Space record is preserved as 5/12, quality
low, but is not a current score claim.

```text
publication_allowed=false
score_claim=false
official_author_endorsement=false
```

## Decision boundaries

- C1 rejects the printed universal equivalence claim, not every possible
  DPO/RLHF relationship.
- C2 and C3 include a small predeclared real-preference pilot; they are not
  full-scale benchmark replications.
- C4's derivation passes, but the scaled learned-policy improvement gate fails
  and remains part of the record.
- C6 cannot be independently tested without generations, judgments, dataset
  identity, and evaluator revisions.
- The 5/12 Space score is historical and archived.

The claim contracts, raw results, controls, and release hashes remain
unchanged; this dossier makes their scope explicit.
