# Claim 5 — soft-margin ranking limit

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

- [Raw certificate](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/raw/formal_audit_C2_C5.json)
- [Contract](https://huggingface.co/spaces/DineshAI/7UEBX1KU1y/resolve/main/evidence/contracts/C5.json)

Limitation: this asymptotic identity does not establish model behavior at a particular finite beta.
