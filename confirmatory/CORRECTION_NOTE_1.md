# Correction Note 1: Withdrawal of the Mini-Round Decision M2

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

1. The mini-round (PREREGISTRATION_MINIROUND.md, SHA-256 3b6702f683023611d6f4a7549317d3e11be674fff08a85ed451bf46969df5492) reported, under rule M2, the decision
   **"no detectable curvature effect"** (hyperbolic term 0.007, 95% interval -0.032 to 0.046, 13 degrees of freedom).
2. That decision is **withdrawn**. The Euclidean plane has no length scale, so the Euclidean conditions at disk radii 0.30 and 0.40 with the same design boundary share are the same problem (they gave the same K).
   The 18 conditions contained 3 duplicates, so the effective sample was 15 conditions and the degrees of freedom were 10, not 13.
3. After the duplicates were removed (a post hoc analysis, decided after the result was seen) the interval of the hyperbolic term was -0.058 to 0.060, and the decision is **inconclusive**. The Spearman correlation of M1 was 0.30 (one-sided permutation p = .143, inconclusive; as preregistered with duplicates: 0.31, p = .103) and the mean absolute error of M3 was 0.028 (the model fitted on three Euclidean conditions, not six).
4. The decisions as originally computed are kept in the data (mini_decisions.json) and are reported next to the corrected analysis. The follow-up (PREREGISTRATION_FOLLOWUP.md, SHA-256 d8a5f5101148869a4a39c91c4e1a64f938a41a2f96caa2224c0b49b281334a0b) was designed to add power and is the later test.
5. No file hashed earlier is edited.
