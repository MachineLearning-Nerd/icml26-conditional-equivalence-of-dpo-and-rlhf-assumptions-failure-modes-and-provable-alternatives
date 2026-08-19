# Reproduction environment

## Fixed command

```bash
uv sync --frozen
uv run --frozen python -m reproduction.run
```

The release verifier is:

```bash
uv run --frozen python evidence/code/release_verifier.py
```

The collection-surface verifier is:

```bash
python3 verify_final.py
```

## Recorded run

- Python: `3.12.11`
- NumPy: `2.3.2`
- Platform: macOS arm64
- Visible CPUs: `8`
- Threads: `1`
- Seed: `260520834`
- Dataset revision: `9d189bae5856a823f3708d2c2bc4dbb43c90eb11`
- Dataset subset SHA-256: `1be7454542bc51886dc0cf1c5bed5d1c6cf10f4812685f9f09fa66c93e66fab4`
- Recorded release runtime: `15.669838166970294` seconds

The release used CPU-only, deterministic scalar theory, exact counterexample,
small preference-pilot, and benchmark-provenance checks. It did not retrain
the paper's 8B model or fabricate missing benchmark outputs.

## Environment limits

The C6 blocker is an evidence-availability boundary, not a local runtime
failure: generations, judgments, dataset identity, and exact evaluator
revisions are unavailable. The C4 scaled learned-policy improvement failure is
retained as negative evidence rather than hidden by the passing derivation
checks.
