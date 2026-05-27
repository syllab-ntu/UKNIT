# Section 6 Cryptanalysis Mapping

This file maps the paper's Section 6 cryptanalysis claims to the organized
source files in this directory. The historical search scripts are preserved
as research-generation code; `section6/reproduce.py` is the reviewer-facing,
standard-library entry point that prints and checks the reported results.

Run:

```bash
python3 section6/reproduce.py
```

The package-level entry point also includes this mapping:

```bash
python3 cryptanalysis_clean.py --section6
```

## Mapping

| Paper section | Topic | Primary source files | Reviewer result |
| --- | --- | --- | --- |
| 6.1 | Simple differential cryptanalysis | `differential/maindiff.py`, `key-recovery/keyrecoverydist.py`, `key-recovery/keyrecoverydist_search.py`, `differentialattack.py`, `QuasiDiff/quasi.py` | Table 2 differential bounds; W(0,10) key recovery with time `2^110` and data `2^55.7`; quasi-differential confirmation for W(2,8). |
| 6.2 | Multiple differential cryptanalysis | `differential_effect/diffeffect.py`, `differential_effect/diffeffectcount.py`, `differential_effect/extract.py` | 100 characteristics over W(2,8), 72 differentials, 3 DTPs, best clustered probability about `2^-63.3`. |
| 6.3 | Linear and linear hull cryptanalysis | `linear/linear.py`, `linear/linear_keyrec.py`, `linearhull/linearhull.py`, `linearhull/linearcount.py`, `linearattack.py` | Table 2 linear bounds; W(2,8) best ELP about `2^-62.4`. |
| 6.4 | Impossible differential cryptanalysis | `impossible/impossible.py`, `impossible/impossible_check.py`, `impossible/idkeyrecovery-1.py`, `impossible/idkeyrecovery-2.py`, `differentialattack.py` | Two W(3,7) impossible truncated differentials; W(1,10) key recovery with time `2^93` and data `2^55`. |
| 6.5 | Zero-correlation cryptanalysis | `zerocorrelation/zerocorrelation.py`, `zerocorrelation/checkmatrix.py`, `linearattack.py` | Two W(3,7) zero-correlation hulls matching the impossible-differential patterns. |
| 6.6 | Integral attacks | `integral/integral.py`, `divisionproperty.py` | Longest zero-sum property is 7 rounds; no W(i,8) zero-sum or key-aware one-sum property found. |
| 6.7 | Demirci-Selcuk MITM | `DS-MITM/MITM.py`, `DS-MITM/checksbox.py`, `mitm.py` | W(0,9) attack with time about `2^87`, data `2^61`, and memory `2^34` blocks. |
| 6.8 | Boomerang and rectangle attacks | `Boomerang/boom.py`, `Boomerang/boomkey.py`, `boomerang.py` | Best 8-round rectangle estimate `2^-141`; best 7-round estimate `2^-116`. |
| 6.9 | Differential-linear attacks | `Diff-Linear/DL.py`, `difflinear.py` | W(1,9) key recovery with time `2^92.6` and data `2^53.6`; best 8-round DL distinguisher is not threatening. |
| 6.10 | Invariant attack | No dedicated search script | Structural argument based on the key schedule. |
| 6.11 | Slide and internal differential attacks | No dedicated search script | Structural argument based on non-aligned round functions. |

## Notes

The historical scripts build SAT/Gurobi search artifacts and may require local
solver tooling.  Generated LaTeX/worksheet artifacts have been removed from the
clean tree.  The reviewer-facing reproduction layer does not rerun expensive
searches; it records the Section 6 outputs and checks their internal
consistency, table shapes, best-window claims, and complexity exponents.
