# Executive summary

This release replaces the judged 5/12 scalar interpretation with exact claim
contracts, executable fail-closed checks, a real-preference learned-policy
experiment, and an explicit benchmark blocker. It preserves every file and page
from the judged Space revision `73b1ac8ff5dd201847e1e11cccc0ee0514beb728`.

| Claim | Final state | Evidence |
| --- | --- | --- |
| [C1](#/claim-1) | **FALSIFIED** | Exact finite-policy counterexample |
| [C2](#/claim-2) | **VERIFIED** | Exact objective certificate + 9 real-data runs |
| [C3](#/claim-3) | **VERIFIED** | Exact U witness + 9 real-data trajectories |
| [C4](#/claim-4) | **VERIFIED** | Direct constrained-RLHF differentiation |
| [C5](#/claim-5) | **VERIFIED** | Uniform softplus-to-hinge error bound |
| [C6](#/claim-6) | **BLOCKED** | Four-route audit; checkpoint found, generations absent |

## Main finding

The paper's universal conditional-equivalence theorem is **FALSIFIED as
written**: with a uniform reference, reward gap 1, and beta 1, the boundary
condition holds and RLHF has finite optimum delta 1, yet the printed DPO loss
has negative derivative there and is strictly smaller at finite delta 2.

Claims 2–5 survive at their exact stated scopes. C2 and C3 additionally pass a
predeclared CPU-scaled experiment on 512 real chosen/rejected pairs from the
paper dataset. C4's exact derivation passes, while its scaled comparative model
gate fails and remains visible. C6 is **BLOCKED** after four routes: a likely
first-author checkpoint is now frozen, but no benchmark generations,
judgments, or exact evaluator revisions permit independent evaluation.

## Scope and cost

- Fixed command: `uv sync --frozen && uv run --frozen python -m reproduction.run`
- Git commit: `e8505d6cb1bfa5679eea18690d9a5e8496b46fd9`
- Python 3.12.11; NumPy 2.3.2; one CPU thread
- Seed: 260520834; runtime: 15.670 s
- Dataset revision: `9d189bae5856a823f3708d2c2bc4dbb43c90eb11`
- Dataset subset hash: `1be7454542bc51886dc0cf1c5bed5d1c6cf10f4812685f9f09fa66c93e66fab4`
- GPU used: **none**

Raw JSON, code, contracts, lockfile, and release manifest are downloadable from
the [evidence directory](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/release_manifest.json). Trackio artifact
publishing was intentionally not used because this repository's authorized
evidence path is text-only commits.
