# Claim evidence ledger

This ledger records each claim's paper anchor, producer, evidence, controls,
and exact stopping boundary. The original contracts remain under
[`evidence/contracts/`](evidence/contracts/); the current machine-readable
status is in [`evidence/raw/claim_statuses.json`](evidence/raw/claim_statuses.json).

Overall status: `PARTIAL_CLAIMS_C1_FALSIFIED_C2_TO_C5_VERIFIED_SCOPED_C6_BENCHMARK_BLOCKED`.

Publication boundary:
`C1_PRINTED_ORDERED_PAIR_COUNTEREXAMPLE_C4_SCALED_LEARNED_POLICY_GATE_FAILED_C6_MISSING_GENERATIONS_JUDGMENTS_EVALUATOR_REVISIONS`.

| Claim | Paper anchor | Producer and primary evidence | Independent checks and controls | Scoped result and boundary |
| --- | --- | --- | --- | --- |
| C1 | Conditional equivalence theorem and printed DPO/RLHF objective | `evidence/code/claim1_counterexample.py`; `evidence/raw/claim1_counterexample.json`; `pages/claim-1/page.md` | Checks all theorem premises and strict boundary, then evaluates the printed DPO loss at the RLHF optimum and a finite perturbation | `FALSIFIED`; the printed universal equivalence claim fails for the ordered-pair objective. This does not falsify every DPO/RLHF relationship or alternative population objective. |
| C2 | Relative objective under the failure mode | `evidence/code/formal_audit.py` and `evidence/code/preference_pilot.py`; `evidence/raw/formal_audit_C2_C5.json`, `real_preference_pilot.json` | Exact objective identities, derivative checks, and predeclared nine-run real-preference pilot | `VERIFIED_SCOPED`; finite exact algebra and pilot evidence, not a universal benchmark claim. |
| C3 | Undesirable solution region | `evidence/code/formal_audit.py` and `evidence/code/preference_pilot.py`; `evidence/raw/formal_audit_C2_C5.json`, `real_preference_pilot.json` | Exact witness/monotonicity checks and real-data trajectories entering the declared region | `VERIFIED_SCOPED`; the pilot is small and CPU-scaled. |
| C4 | Constrained-RLHF stationary loss | `evidence/code/formal_audit.py`; `evidence/raw/formal_audit_C2_C5.json`; `pages/claim-4/page.md` | Direct differentiation, finite-difference control, omission controls, and the `gamma=0` DPO reduction | `VERIFIED_SCOPED`; the scaled learned-policy improvement gate fails and remains visible as negative evidence. |
| C5 | Soft-margin ranking limit | `evidence/code/formal_audit.py`; `evidence/raw/formal_audit_C2_C5.json`; `pages/claim-5/page.md` | Uniform `0 <= softplus(beta*a)/beta - max(0,a) <= log(2)/beta` certificate with boundary and reversed-argument controls | `VERIFIED_SCOPED`; analytic certificate and finite controls only. |
| C6 | Benchmark performance | `evidence/code/benchmark_audit.py`; `evidence/raw/benchmark_audit_C6.json`; `pages/claim-6/page.md` | Paper-table transcription/arithmetic audit, four provenance routes, checkpoint metadata, and evaluator-availability checks | `BLOCKED`; no generations, judgments, dataset identity, or exact evaluator revisions support an independent benchmark run. |

The evidence path is:

```text
paper anchor → claim contract → producer → raw result
             → checker/control → scoped status
```

The historical 5/12 judge record is a separate archived observation and is
not used to upgrade or downgrade the claim contracts.
