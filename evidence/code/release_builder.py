import hashlib
import json
import shutil
import subprocess
from pathlib import Path


SPACE_ID = "DineshAI/7UEBX1KU1y"
JUDGED_REVISION = "73b1ac8ff5dd201847e1e11cccc0ee0514beb728"
FIXED_COMMAND = "uv sync --frozen && uv run --frozen python -m reproduction.run"
RAW_BASE = f"https://huggingface.co/spaces/{SPACE_ID}/resolve/main/evidence"


def write_text(root, relative_path, content):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")
    return path


def copy_text(root, source, relative_path):
    return write_text(root, relative_path, source.read_text())


def git_sha(repo_root):
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def claim_table(claims):
    rows = ["| Claim | Final state | Evidence |", "| --- | --- | --- |"]
    evidence = {
        "C1": "Exact finite-policy counterexample",
        "C2": "Exact objective certificate + 9 real-data runs",
        "C3": "Exact U witness + 9 real-data trajectories",
        "C4": "Direct constrained-RLHF differentiation",
        "C5": "Uniform softplus-to-hinge error bound",
        "C6": "Four-route audit; checkpoint found, generations absent",
    }
    for claim in claims:
        rows.append(f"| [{claim['id']}](#/claim-{claim['id'][1:]}) | **{claim['status']}** | {evidence[claim['id']]} |")
    return "\n".join(rows)


def build_pages(bundle, outputs, repo_root):
    claims = json.loads((outputs / "claim_statuses.json").read_text())
    claim1 = json.loads((outputs / "claim1_counterexample.json").read_text())
    formal = json.loads((outputs / "formal_audit_C2_C5.json").read_text())
    pilot = json.loads((outputs / "real_preference_pilot.json").read_text())
    benchmark = json.loads((outputs / "benchmark_audit_C6.json").read_text())
    metadata = json.loads((outputs / "run_metadata.json").read_text())
    aggregate = pilot["aggregate"]
    commit = git_sha(repo_root)

    write_text(
        bundle,
        "pages/index.md",
        """# Conditional Equivalence of DPO and RLHF — reproduction

## Pages

| Page |
| --- |
| [Executive summary](#/executive-summary) |
| [Claim 1 — conditional equivalence](#/claim-1) |
| [Claim 2 — relative objective](#/claim-2) |
| [Claim 3 — undesirable region](#/claim-3) |
| [Claim 4 — CPO derivation](#/claim-4) |
| [Claim 5 — soft-margin limit](#/claim-5) |
| [Claim 6 — benchmarks](#/claim-6) |
| [Conclusion](#/current-conclusion) |
| [Historical rejected baseline notice](#/historical-notice) |
| [Historical overview](#/overview) |
| [Historical claims](#/claims) |
| [Historical evidence](#/evidence) |
| [Historical conclusion](#/conclusion) |
| [Historical verification run](#/verification-run) |""",
    )
    write_text(
        bundle,
        "pages/executive-summary/page.md",
        f"""# Executive summary

This release replaces the judged 5/12 scalar interpretation with exact claim
contracts, executable fail-closed checks, a real-preference learned-policy
experiment, and an explicit benchmark blocker. It preserves every file and page
from the judged Space revision `{JUDGED_REVISION}`.

{claim_table(claims)}

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

- Fixed command: `{FIXED_COMMAND}`
- Git commit: `{commit}`
- Python {metadata['python']}; NumPy {metadata['numpy']}; one CPU thread
- Seed: {metadata['seed']}; runtime: {metadata['total_runtime_seconds']:.3f} s
- Dataset revision: `{pilot['dataset_revision']}`
- Dataset subset hash: `{pilot['subset_sha256']}`
- GPU used: **none**

Raw JSON, code, contracts, lockfile, and release manifest are downloadable from
the [evidence directory]({RAW_BASE}/release_manifest.json). Trackio artifact
publishing was intentionally not used because this repository's authorized
evidence path is text-only commits.
""",
    )
    c1 = claim1["counterexample"]
    write_text(
        bundle,
        "pages/claim-1/page.md",
        f"""# Claim 1 — conditional equivalence

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
| {c1['beta']} | {c1['reward_gap']} | {c1['delta_ref']} | {c1['rlhf_delta_star']} | {c1['competitor_delta']} |

The strict boundary holds. RLHF's objective is {c1['rlhf_objective_at_rlhf_star']:.6f}
at delta 1 versus {c1['rlhf_objective_at_competitor']:.6f} at delta 2. The DPO
loss moves the other way: {c1['dpo_loss_at_rlhf_star']:.6f} to
{c1['dpo_loss_at_competitor']:.6f}, with derivative
{c1['dpo_derivative_at_rlhf_star']:.6f} at the RLHF optimum. Hence that optimum
is not even stationary for the stated DPO objective.

Independent routes in one certificate: exact SMT premises, direct RLHF
first/second-order checks, a finite lower-loss DPO competitor, and three
mutation controls. Any failure returns `BLOCKED` and exits nonzero.

- [Raw certificate]({RAW_BASE}/raw/claim1_counterexample.json)
- [Contract]({RAW_BASE}/contracts/C1.json)
- [Executable checker]({RAW_BASE}/code/claim1_counterexample.py)

## Limitation

This falsifies the ordered-pair objective printed in the theorem. A different
population cross-entropy that explicitly averages both stochastic labels for
the same pair is outside this contract.
""",
    )
    write_text(
        bundle,
        "pages/claim-2/page.md",
        f"""# Claim 2 — relative objective under failure

**Final state: VERIFIED · confidence: HIGH**

For all `beta>0`, positive reward gaps, and finite references satisfying
`delta_ref <= -reward_gap/beta`, exact-real arithmetic proves the RLHF identity
has `delta_star<=0`. The DPO argument is invariant to an arbitrary common shift
of policy and reference log odds, and its derivative is strictly negative at
every finite delta. This verifies optimization of relative advantage and the
objective-level distinction.

The real-data route trained nine paired policies (3 seeds × 3 corrupted
references) on 384 train and 128 held-out pairs. Its predeclared C2 gate passed:
all DPO runs lowered the objective and at least one learned reference was
misaligned on held-out pairs.

- [Formal raw certificate]({RAW_BASE}/raw/formal_audit_C2_C5.json)
- [Real-data raw runs]({RAW_BASE}/raw/real_preference_pilot.json)
- [Contract]({RAW_BASE}/contracts/C2.json)

Limitation: unconstrained DPO eventually pushes a scalar delta upward; this
claim distinguishes objectives and does not assert permanent misalignment.
""",
    )
    write_text(
        bundle,
        "pages/claim-3/page.md",
        f"""# Claim 3 — undesirable solution region

**Final state: VERIFIED · confidence: HIGH**

With `delta_ref < -reward_gap/beta`, the exact witness `delta_ref/2` lies in
`U={{delta_ref<delta<0}}`: it still prefers the rejected response but has lower
DPO loss than the reference. Exact monotonicity and boundary controls pass.

On the real paper dataset, all nine DPO trajectories lowered loss and at least
one entered U, satisfying the predeclared C3 gate. The observed maximum U
fractions ranged from {min(run['dpo']['max_train_undesirable_fraction'] for run in pilot['runs']):.3f}
to {max(run['dpo']['max_train_undesirable_fraction'] for run in pilot['runs']):.3f}.

- [Formal raw certificate]({RAW_BASE}/raw/formal_audit_C2_C5.json)
- [Real-data trajectories]({RAW_BASE}/raw/real_preference_pilot.json)
- [Contract]({RAW_BASE}/contracts/C3.json)

Limitation: for fixed finite `delta_ref`, the gradient factor's limit at the
zero boundary is positive, not literally zero. The release verifies weakening,
not an exact zero-gradient statement.
""",
    )
    write_text(
        bundle,
        "pages/claim-4/page.md",
        f"""# Claim 4 — constrained-RLHF stationary loss

**Final state: VERIFIED · confidence: MEDIUM**

Direct differentiation of the two-response constrained-RLHF objective recovers
the paper's inverse-probability adaptive margin. The analytic first-order
residual is {formal['C4']['raw']['analytic_derivative']:.1f}; a central finite
difference gives {formal['C4']['raw']['finite_difference_derivative']:.3e}.
Omitting the margin breaks the condition, replacing optimal-policy
probabilities with reference probabilities makes it stationary, and `gamma=0`
recovers DPO.

The scaled learned-policy comparison is retained as negative evidence: at
`gamma=0.02`, mean DPO/CPO held-out accuracy was
{aggregate['mean_dpo_accuracy']:.4f}/{aggregate['mean_cpo_accuracy']:.4f}, and
mean escape rate was {aggregate['mean_dpo_escape_rate']:.4f}/{aggregate['mean_cpo_escape_rate']:.4f}.
The predeclared empirical C4 improvement gate therefore failed. This does not
contradict the narrower derivation contract.

- [Formal certificate]({RAW_BASE}/raw/formal_audit_C2_C5.json)
- [Failed empirical gate]({RAW_BASE}/raw/real_preference_pilot.json)
- [Contract]({RAW_BASE}/contracts/C4.json)

Limitation: no global convergence or absolute-advantage theorem is claimed by
this reproduction state.
""",
    )
    write_text(
        bundle,
        "pages/claim-5/page.md",
        """# Claim 5 — soft-margin ranking limit

**Final state: VERIFIED · confidence: HIGH**

For every fixed finite `a=delta_ref-delta` and every positive beta, the checker
uses the uniform certificate

```text
0 <= softplus(beta*a)/beta - max(0,a) <= log(2)/beta.
```

The upper bound tends to zero, proving the paper's limit without relying on a
finite grid. Boundary, sign, normalization, and reversed-argument controls all
pass. The hinge threshold is `delta_ref`, so it is negative whenever the
reference log odds are negative.

- [Raw certificate](""" + RAW_BASE + "/raw/formal_audit_C2_C5.json)\n- [Contract](" + RAW_BASE + "/contracts/C5.json)\n\nLimitation: this asymptotic identity does not establish model behavior at a particular finite beta.\n",
    )
    routes = benchmark["routes"]
    write_text(
        bundle,
        "pages/claim-6/page.md",
        f"""# Claim 6 — benchmark performance

**Final state: BLOCKED · confidence: LOW**

The narrower source statement is verified: CPO has the largest point estimate
in the paper's table (25.15 AlpacaEval WR, 26.57 LC, 32.6 Arena-Hard), and all
four claimed arithmetic differences recompute exactly. Independent benchmark
reproduction remains blocked after the mandatory routes:

1. **Source table:** PASS — {routes[0]['result']}
2. **Artifact provenance:** BLOCKED — {routes[1]['result']}
3. **Official benchmark execution:** BLOCKED — {routes[2]['result']}
4. **Falsification attempt:** INCONCLUSIVE — {routes[3]['result']}

The CPO Arena-Hard 90% interval `[30.7,35.0]` overlaps SimPO's `[27.3,32.3]`.
No AlpacaEval intervals or paired judgments are supplied. The immutable 16.06
GB checkpoint makes model provenance materially stronger, but its model card
does not link the paper and supplies no benchmark outputs. Full-suite GPU
execution is outside campaign authorization, and the paper omits exact judge
revisions needed for a claim-faithful rerun.

- [Four-route raw audit]({RAW_BASE}/raw/benchmark_audit_C6.json)
- [Contract]({RAW_BASE}/contracts/C6.json)

This is a durable blocker, not an estimate and not a hidden failure.
""",
    )
    write_text(
        bundle,
        "pages/current-conclusion/page.md",
        f"""# Conclusion

The strongest honest outcome is **4 VERIFIED · 1 FALSIFIED · 1 BLOCKED**.

- C1's universal theorem fails on a finite exact counterexample satisfying its boundary.
- C2 and C3 pass both exact checks and a real-preference learned-policy route.
- C4's stationary adaptive-margin derivation passes, while its scaled comparative model gate fails and remains disclosed.
- C5 has a uniform asymptotic error certificate.
- C6's author-reported ranking is internally correct and a likely author checkpoint is frozen, but independent benchmark evidence is unavailable.

Every result comes from `{FIXED_COMMAND}` at commit `{commit}` with one CPU
thread and no GPU. Download the [release manifest]({RAW_BASE}/release_manifest.json)
or rerun the [fail-closed verifier]({RAW_BASE}/code/release_verifier.py).

The historical 5/12 pages remain reachable below and are explicitly labeled as
the rejected scalar baseline. No historical file or claim was deleted.
""",
    )
    write_text(
        bundle,
        "pages/historical-notice/page.md",
        f"""# Historical rejected baseline

The pages that follow are preserved byte-for-byte from judged revision
`{JUDGED_REVISION}` for auditability. Their statements that five claims were
fully verified and “FULL_GATE_READY” were rejected by the live judge, which
awarded 5/12 and classified the five theory checks as toy evidence. They are
historical records only and must not be read as the current conclusion.
""",
    )

    children = [
        {"slug": "executive-summary", "title": "Executive summary", "file": "pages/executive-summary/page.md", "children": []},
        *[
            {"slug": f"claim-{number}", "title": f"Claim {number}", "file": f"pages/claim-{number}/page.md", "children": []}
            for number in range(1, 7)
        ],
        {"slug": "current-conclusion", "title": "Conclusion", "file": "pages/current-conclusion/page.md", "children": []},
        {"slug": "historical-notice", "title": "Historical rejected baseline — notice", "file": "pages/historical-notice/page.md", "children": []},
        {"slug": "overview", "title": "Historical rejected baseline — overview", "file": "pages/overview/page.md", "children": []},
        {"slug": "claims", "title": "Historical rejected baseline — claims", "file": "pages/claims/page.md", "children": []},
        {"slug": "evidence", "title": "Historical rejected baseline — evidence", "file": "pages/evidence/page.md", "children": []},
        {"slug": "conclusion", "title": "Historical rejected baseline — conclusion", "file": "pages/conclusion/page.md", "children": []},
        {"slug": "verification-run", "title": "Historical rejected baseline — verification run", "file": "pages/verification-run/page.md", "children": []},
    ]
    logbook = {
        "schema_version": 1,
        "title": "7UEBX1KU1y — exact and real-preference reproduction",
        "emoji": "🔬",
        "space_id": SPACE_ID,
        "paper": None,
        "tags": ["icml2026-repro", "paper-7UEBX1KU1y"],
        "updated_at": "2026-07-31T00:00:00+00:00",
        "root": {
            "slug": "index",
            "title": "7UEBX1KU1y — exact and real-preference reproduction",
            "file": "pages/index.md",
            "children": children,
        },
        "agent_view_tokens": 6000,
        "revision": f"release-{commit[:12]}",
    }
    write_text(bundle, "logbook.json", json.dumps(logbook, indent=2, ensure_ascii=False))


def build_evidence(bundle, outputs, repo_root):
    for source in sorted((repo_root / "reproduction").glob("*.py")):
        copy_text(bundle, source, f"evidence/code/{source.name}")
    for source in sorted((repo_root / "evidence" / "claim_contracts").glob("*.json")):
        copy_text(bundle, source, f"evidence/contracts/{source.name}")
    for name in (
        "historical_scalar_checks.json",
        "claim1_counterexample.json",
        "formal_audit_C2_C5.json",
        "real_preference_pilot.json",
        "benchmark_audit_C6.json",
        "claim_statuses.json",
        "run_metadata.json",
        "manifest.json",
    ):
        copy_text(bundle, outputs / name, f"evidence/raw/{name}")
    for name in ("source_manifest.json", "c6_checkpoint_manifest.json", "judged_snapshot_manifest.json", "judged_verdict.json", "empirical_protocol.json"):
        copy_text(bundle, repo_root / "evidence" / name, f"evidence/{name}")
    copy_text(bundle, repo_root / "pyproject.toml", "evidence/environment/pyproject.toml")
    copy_text(bundle, repo_root / "uv.lock", "evidence/environment/uv.lock")
    write_text(bundle, "evidence/verification_command.txt", FIXED_COMMAND)

    manifest = {}
    for path in sorted(bundle.rglob("*")):
        if path.is_file():
            manifest[str(path.relative_to(bundle))] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_text(bundle, "evidence/release_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))


def build_release_bundle(repo_root, outputs):
    bundle = repo_root / "release" / "space"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    build_pages(bundle, outputs, repo_root)
    build_evidence(bundle, outputs, repo_root)
    return bundle
