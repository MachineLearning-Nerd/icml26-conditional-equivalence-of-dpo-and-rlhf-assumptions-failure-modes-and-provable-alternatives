# Branch audit

This repository keeps the complete evidence-development history. The old `orx/` prefix was an internal experiment namespace; the branches below are renamed to describe their role. Branch-specific work is preserved, while `main` is the aggregate release branch.

| Clean branch | Previous branch | Evidence or purpose |
| --- | --- | --- |
| `main` | `main` | Aggregate release at the current C1–C6 verdicts, release manifest, readable claim pages, and fail-closed verifier. |
| `audit/c6-author-checkpoint-provenance` | `orx/c6-author-checkpoint-provenance-audit` | Audits the likely first-author CPO checkpoint, pins its immutable Hub revision, and records why model provenance still does not provide benchmark generations or evaluator provenance. |
| `release/combined-candidate` | `orx/combined-release-candidate` | Combines the exact algebra audit, C1 counterexample, and real-preference pilot into a candidate release bundle. |
| `experiment/cpo-margin-strength-0-2` | `orx/cpo-margin-strength-0-2` | Tests the CPO margin-strength setting used by the small real-preference pilot. |
| `audit/exact-algebra-c2-c5` | `orx/exact-algebra-audit-c2-c5` | Produces the exact C2–C5 obligations, controls, and raw scalar certificates. |
| `audit/claim-1-proof-obligations` | `orx/exact-claim-1-proof-obligations` | Encodes the C1 theorem premises and finite counterexample that falsifies the printed universal equivalence claim. |
| `audit/judged-scalar-baseline` | `orx/judged-scalar-baseline` | Preserves the initial judged Space snapshot and its 5/12 low-quality baseline as historical evidence. |
| `experiment/real-preference-policy-pilot` | `orx/real-preference-policy-pilot` | Runs the predeclared CPU-scaled pilot over 384 training and 128 held-out preference pairs, with three seeds and three reference-corruption rates. |
| `audit/release-bundle-gate` | `orx/release-bundle-gate-audit` | Adds the release manifest, source and environment records, claim-status aggregation, and fail-closed verification gate. |

## Branch guarantees

- No evidence-development branch was discarded during cleanup.
- The old names are retained in this table only as migration history; the live GitHub branches use the clean names above.
- `main` is the default branch and contains the human-readable README, this audit, the current claim pages, and the final release bundle.
- Commit attribution for the rewritten reachable history is normalized to `MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>`; the evidence content itself is unchanged except for documentation and repository-link cleanup.
