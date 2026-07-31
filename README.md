# Conditional Equivalence of DPO and RLHF — reproduction

Reproduction for ICML 2026 paper 7UEBX1KU1y / arXiv:2605.20834.

Run every experiment with the frozen command:

```bash
uv sync --frozen && uv run --frozen python -m reproduction.run
```

The root experiment reconstructs the judged scalar baseline. Its checks are
historical controls, not sufficient evidence for the paper claims.
