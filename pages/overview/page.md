# overview


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_9ee605d7d756", "created_at": "2026-07-30T01:22:14+00:00", "title": "Overview"}
-->
# 7UEBX1KU1y — Conditional Equivalence of DPO and RLHF

**arXiv 2605.20834 · ICML 2026 · 5/6 anchored claims VERIFIED = 10 pts (C5 benchmark deferred)**

DPO=RLHF equivalence is CONDITIONAL: holds iff δ_ref > −Δr*/β (RLHF-optimal prefers the human-preferred
response). When the reference is misaligned, DPO optimizes RELATIVE advantage (δ−δ_ref), can converge to
UNDESIRABLE policies (δ<0), and acts as margin-ranking with a NEGATIVE target margin. CPO enforces δ≥0.

**Reproduction:** scalar algebra in δ-space (δ=log π(y_w)−log π(y_l)). All theory claims machine-exact.
