# verification-run


---
<!-- trackio-cell
{"type": "code", "id": "cell_3c6d2e37bd12", "created_at": "2026-07-30T01:22:16+00:00", "title": "verify 5 claims", "command": ["python3", "repro/src/verify.py"], "exit_code": 0, "duration_s": 0.138}
-->
````bash
$ python3 repro/src/verify.py
````

exit 0 · 0.1s


````python title=verify.py
"""
Independent verification of the 5 anchored claims of paper 7UEBX1KU1y
("Conditional Equivalence of DPO and RLHF", arXiv:2605.20834).

All claims are scalar algebra in delta-space (delta = log pi(yw|x) - log pi(yl|x), the preference
strength).  Reward gap Delta_r = r*(yw)-r*(yl) > 0 (humans prefer yw), temperature beta, reference
delta_ref.  RLHF-optimal delta_* = delta_ref + Delta_r/beta;  DPO loss L = -log sigma(beta*(delta-delta_ref)).
Pure numpy, CPU.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import core as M

BETA = 1.0
DELTA_R = 2.0      # reward gap (humans prefer yw)
results = []


def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# --------------------------------------------------------------------------- C0
def claim_C0():
    """Theorem 3.5: DPO=RLHF equivalence  <=>  delta_ref > -Delta_r/beta  ( <=> delta_* > 0).
    Scan delta_ref across the boundary -Delta_r/beta and check the equivalence flips exactly there."""
    boundary = -DELTA_R / BETA
    ok = True
    detail = []
    for dref in [2.0, 0.0, boundary + 0.5, boundary - 0.5, -3.0]:
        ds = M.delta_star(dref, DELTA_R, BETA)
        eq = M.equivalence_holds(dref, DELTA_R, BETA)
        expect = (ds > 0)
        ok = ok and (eq == expect)
        detail.append(f"dref={dref:+.1f}->d*={ds:+.2f},eq={eq}")
    # exactly at the boundary delta_* = 0 (indifferent) -> equivalence fails (strict >)
    check("C0 Thm3.5 equivalence iff delta_ref > -Dr/beta", ok,
          f"boundary={boundary:+.2f}; " + "; ".join(detail))


# --------------------------------------------------------------------------- C1
def claim_C1():
    """When equivalence fails, DPO optimizes RELATIVE advantage (delta-delta_ref) -> delta->infty,
    diverging from RLHF's delta_* (< 0).  L_DPO is a function of (delta-delta_ref) only."""
    dref = -3.0                                     # fails: dref < -Dr/beta = -2
    ds = M.delta_star(dref, DELTA_R, BETA)          # RLHF optimum ( < 0 )
    traj = M.descend(lambda d: M.dpo_loss(d, dref, BETA), delta0=dref + 0.1, lr=0.05, steps=6000)
    dpo_final = traj[-1]
    diverges = (dpo_final > 1.0) and (ds < 0.0)     # DPO -> large positive, RLHF -> negative
    # relative-advantage structure: L_DPO(delta) == L_DPO(delta+c, delta_ref+c) for any c
    c = 0.7
    rel_sym = abs(M.dpo_loss(1.0, 0.5, BETA) - M.dpo_loss(1.0 + c, 0.5 + c, BETA)) < 1e-9
    check("C1 DPO optimizes relative advantage (diverges from RLHF d*)", diverges and rel_sym,
          f"dref={dref}: RLHF d*={ds:+.2f} (<0) vs DPO descent -> delta={dpo_final:+.2f}; "
          f"loss shift-invariant in (delta-delta_ref): {rel_sym}")


# --------------------------------------------------------------------------- C2
def claim_C2():
    """Def 3.3 / Prop 3.4: U={delta<0, delta>delta_ref} non-empty iff delta_ref<0; DPO gradient
    factor sigma(-beta(delta-delta_ref)) vanishes as delta grows past delta_ref (trapping mechanism)."""
    ne_pos = M.undesirable_space_nonempty(-2.0)     # delta_ref<0 -> non-empty
    ne_neg = not M.undesirable_space_nonempty(0.5)  # delta_ref>0 -> empty
    # a concrete policy in U
    dref = -2.0; d_in_U = -1.0
    in_U = M.in_undesirable_space(d_in_U, dref)
    # gradient factor decreases as delta moves past delta_ref toward 0 (vanishing -> slow escape)
    factors = [M.dpo_grad_factor(d, dref, BETA) for d in (-1.5, -1.0, -0.5, 0.0)]
    vanishes = factors[0] > factors[-1]             # monotonically decreasing
    ok = ne_pos and ne_neg and in_U and vanishes
    check("C2 undesirable space U non-empty + gradient vanishing", ok,
          f"U nonempty(dref=-2)={ne_pos}, empty(dref=+0.5)={ne_neg}; delta=-1 in U={in_U}; "
          f"grad factors {np.round(factors,3).tolist()} (decreasing)")


# --------------------------------------------------------------------------- C3
def claim_C3():
    """CPO adds an adaptive margin Psi_cons so the EFFECTIVE margin target delta_ref + Psi_cons/beta >= 0,
    enforcing absolute advantage (delta>=0); DPO (Psi_cons=0) leaves the target = delta_ref (< 0 possible)."""
    dref = -3.0
    psi = -BETA * dref                              # adaptive: cancels the reference bias
    target_cpo = M.cpo_effective_margin_target(dref, BETA, psi)   # >= 0
    target_dpo = M.cpo_effective_margin_target(dref, BETA, 0.0)   # = delta_ref < 0
    # CPO descent escapes U (delta -> > 0)
    traj = M.descend(lambda d: M.cpo_loss(d, dref, BETA, psi), delta0=dref + 0.1, lr=0.05, steps=6000)
    ok = (target_cpo >= -1e-9) and (target_dpo < 0) and (traj[-1] > 0)
    check("C3 CPO adaptive margin enforces absolute advantage (delta>=0)", ok,
          f"dref={dref}: CPO target={target_cpo:+.2f} (>=0) vs DPO target={target_dpo:+.2f} (<0); "
          f"CPO descent -> delta={traj[-1]:+.2f}")


# --------------------------------------------------------------------------- C4
def claim_C4():
    """DPO = soft margin ranking with target margin m = beta*delta_ref, which is NEGATIVE when
    delta_ref<0 (geometric explanation of preference-violating convergence); CPO's margin is >= 0."""
    m_dpo_bad = M.dpo_as_margin_ranking(-3.0, BETA)         # negative
    m_dpo_ok = M.dpo_as_margin_ranking(0.5, BETA)           # positive
    ok = (m_dpo_bad < 0) and (m_dpo_ok > 0)
    check("C4 DPO margin-ranking target can be negative", ok,
          f"DPO margin m=beta*delta_ref: dref=-3 -> m={m_dpo_bad:+.2f} (<0, perverse), "
          f"dref=+0.5 -> m={m_dpo_ok:+.2f}")


if __name__ == "__main__":
    print("=" * 74)
    print("7UEBX1KU1y  Conditional Equivalence of DPO and RLHF  --  5 claims")
    print("=" * 74)
    claim_C0(); claim_C1(); claim_C2(); claim_C3(); claim_C4()
    print("=" * 74)
    anchors = {
        "C0": "Theorem 3.5 (DPO=RLHF equivalence iff delta_ref > -Delta_r/beta, i.e. delta_* > 0)",
        "C1": "Section 3 (when equivalence fails, DPO optimizes relative advantage over the reference, not absolute alignment)",
        "C2": "Definition 3.3 / Proposition 3.4 (undesirable space U non-empty; DPO gradient vanishes near delta=0)",
        "C3": "Section 4 (CPO adaptive margin enforces absolute advantage delta>=0)",
        "C4": "Section 5 (DPO = soft margin ranking with a possibly-negative target margin beta*delta_ref)",
    }
    claim_records = []
    for cid, anchor in anchors.items():
        sub = [r for r in results if r[0].startswith(cid)]
        ok = bool(sub) and all(r[1] for r in sub)
        claim_records.append({"id": cid, "anchor": anchor,
                              "status": "VERIFIED" if ok else "FAILED",
                              "detail": "; ".join(r[0] for r in sub)})
    n_ver = sum(1 for r in claim_records if r["status"] == "VERIFIED")
    verdict = {
        "paper": "7UEBX1KU1y", "arxiv": "2605.20834",
        "title": "Conditional Equivalence of DPO and RLHF: Implicit Assumption, Failure Modes, and Provable Alignment",
        "claims_verified": n_ver, "claims_total": len(claim_records), "claims_deferred": 1,
        "deferred": ["C5 (CPO state-of-the-art on benchmarks) is an LLM-training benchmark, not CPU-verifiable"],
        "all_verified": n_ver == len(claim_records), "claims": claim_records,
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=2)
    for name, ok, _ in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    npass = sum(1 for _, ok, _ in results if ok)
    print(f"\n{n_ver}/{len(claim_records)} claims VERIFIED ({npass}/{len(results)} checks; C5 deferred)")
    sys.exit(0 if n_ver == len(claim_records) else 1)

````


````output
==========================================================================
7UEBX1KU1y  Conditional Equivalence of DPO and RLHF  --  5 claims
==========================================================================
[PASS] C0 Thm3.5 equivalence iff delta_ref > -Dr/beta: boundary=-2.00; dref=+2.0->d*=+4.00,eq=True; dref=+0.0->d*=+2.00,eq=True; dref=-1.5->d*=+0.50,eq=True; dref=-2.5->d*=-0.50,eq=False; dref=-3.0->d*=-1.00,eq=False
[PASS] C1 DPO optimizes relative advantage (diverges from RLHF d*): dref=-3.0: RLHF d*=-1.00 (<0) vs DPO descent -> delta=+2.69; loss shift-invariant in (delta-delta_ref): True
[PASS] C2 undesirable space U non-empty + gradient vanishing: U nonempty(dref=-2)=True, empty(dref=+0.5)=True; delta=-1 in U=True; grad factors [0.378, 0.269, 0.182, 0.119] (decreasing)
[PASS] C3 CPO adaptive margin enforces absolute advantage (delta>=0): dref=-3.0: CPO target=+0.00 (>=0) vs DPO target=-3.00 (<0); CPO descent -> delta=+5.68
[PASS] C4 DPO margin-ranking target can be negative: DPO margin m=beta*delta_ref: dref=-3 -> m=-3.00 (<0, perverse), dref=+0.5 -> m=+0.50
==========================================================================
  PASS  C0 Thm3.5 equivalence iff delta_ref > -Dr/beta
  PASS  C1 DPO optimizes relative advantage (diverges from RLHF d*)
  PASS  C2 undesirable space U non-empty + gradient vanishing
  PASS  C3 CPO adaptive margin enforces absolute advantage (delta>=0)
  PASS  C4 DPO margin-ranking target can be negative

5/5 claims VERIFIED (5/5 checks; C5 deferred)

````
