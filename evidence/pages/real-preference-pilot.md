# Real-preference learned-policy pilot

This route addresses the judge's central criticism that the historical evidence
used only scalar toy checks. It trains deterministic pairwise text policies on
512 real chosen/rejected pairs from the exact dataset used by the paper,
`princeton-nlp/llama3-ultrafeedback-armorm` at revision
`9d189bae5856a823f3708d2c2bc4dbb43c90eb11`.

The model is a CPU-scaled signed-hash unigram/bigram policy, not Llama-3-8B.
Three seeds and 20%, 40%, and 60% corrupted-reference regimes produce nine
paired DPO/CPO comparisons. Train/test row offsets, hyperparameters, and
predeclared claim gates are in `evidence/empirical_protocol.json`.

The run refuses data if the Hub revision differs before or after Viewer API
retrieval. It records the canonical subset hash, per-run raw metrics, a
gamma-zero identity control, and final gates in
`outputs/real_preference_pilot.json`. Any unmet gate leaves that claim
`BLOCKED`; it is never converted into a pass by narrative interpretation.

```bash
uv sync --frozen && uv run --frozen python -m reproduction.run
```

This route cannot validate the paper's Llama-3-8B AlpacaEval or Arena-Hard
numbers and must not be presented as a benchmark reproduction.
