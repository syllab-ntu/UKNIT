# uKNIT-BC Cryptanalysis Code

This directory holds the cryptanalysis code we wrote for **uKNIT-BC** during
its design and security evaluation (Section 6 of the paper). The structure is
two-layered:

- **Top-level `.py` files** define the cipher model and the *generic*
  SAT/MILP-based attack classes (one class per attack family). `newcipher`
  inherits from all of them, and `UKNITBC` instantiates the cipher.
- **Sub-directories** are the *driver* scripts for each attack family: they
  call into the generic models with concrete parameters (rounds, window,
  active positions, key-recovery split, ...) and collect results.

The directory is **self-contained**: the SAT/Espresso/sbox helper package
`myutility/`, the bit/MILP helpers in `basic.py`, the TikZ helper `LATEX.py`,
and the standalone reference cipher in `uknit/` are all vendored in-tree.
All modules use `__file__`-anchored `sys.path` so they work regardless of
the caller's working directory.

---

## Requirements

**Reviewer-facing reproduction only** (recommended starting point):
Python 3.10+. **No third-party packages, no SAT solver, no Espresso.**
Just clone and run:

```bash
python3 cryptanalysis_clean.py        # inventory + sanity checks + Section 6 mapping
python3 section6/reproduce.py         # Section 6 tables + consistency check
```

**Re-running the SAT/MILP attack searches** (the historical scripts under
`differential/`, `linear/`, `impossible/`, ...) requires:

```bash
pip install -r requirements.txt       # numpy, galois  (Gurobi optional, see file)
```

and these external binaries on `PATH`:

- a SAT solver — default `kissat`, configurable to `cryptominisat`,
  `maplesat`, etc. via `sat.solve(..., solver='...')` in `myutility/sat.py`;
- the `espresso` logic minimizer — used by `myutility/espresso.py` to
  compile S-box CNFs;
- `pdflatex` with the TikZ package — only for compiling generated attack
  figures under `*/LATEX/`.

Only `QuasiDiff/quasi.py` additionally needs `gurobipy` (Gurobi MILP).

---

## Quick entry points

| Command | What it does |
| --- | --- |
| `python3 cryptanalysis_clean.py` | Source inventory + Section 6 mapping + standard-library sanity checks (S-box / linear-layer constants and four test vectors). |
| `python3 cryptanalysis_clean.py --section6` | Print only the Section 6 result summary and source mapping. |
| `python3 section6/reproduce.py` | Section 6 result tables (Table 1/2/3, best-window claims) and internal consistency check. |

See [`SECTION6_MAPPING.md`](SECTION6_MAPPING.md) for the paper→file mapping.

---

## Top-level files

### Vendored helpers (third-party but in-tree)

| Path | Role |
| --- | --- |
| [myutility/](myutility/) | The SAT-based modeling utility package (in-house, also at `github.com/hukaisdu/myutility`; trimmed here to only what this project needs). Provides `myutility.sat.sat` (CNF generation + solver dispatch), `myutility.sbox.sbox` (DDT/LAT/MPT/division-property table generators + CNF encoders), and `myutility.espresso.genConstr` (calls the `espresso` binary to minimize CNFs). Every top-level attack class imports from this package. |
| [LATEX.py](LATEX.py) | Tiny TikZ helper (`class latex`) used by `path.py` to assemble standalone TikZ documents from trail figures. |
| [basic.py](basic.py) | Bit/int helpers (`int_2_bit`, `bit_2_int`, `dot`, `hw`, `preceq`/`succeq`) plus MILP constraint helpers (`apply_ineq_from_01_`, `gen_constr_from_mp_table`, `gen_constr_from_linear_table`) and a 2-adic absolute value (`calculate_2_adic_absolute_value`). Used by `QuasiDiff/quasi.py` and `Tool/keyrecoverytool.py`. |
| [uknit/](uknit/) | Standalone reference implementation of uKNIT-BC (`encrypt`, `decrypt`, `hex_to_nibbles`, `nibbles_to_hex`) plus `model_compat.compare_uknit_bc_model` which AST-parses `uknit_bc.py` and checks its S-box / linear-layer constants against the official reference. Used by `cryptanalysis_clean.py` for the standard-library sanity checks. |

### Cipher model

| File | Role |
| --- | --- |
| [uknit_bc.py](uknit_bc.py) | **The uKNIT-BC instance.** Hard-codes the per-round S-boxes and the bit-level linear layer (`UKNIT_BC_MODEL`) and exposes them through `sbox(r,i)` / `matrix(r)`. This is the constant table that the vendored `uknit/` reference checks against. |
| [newcipher.py](newcipher.py) | Base class. Multiply inherits from `linearattack`, `differentialattack`, `boomerang`, `difflinear`, `rkdiffattack`, `divisionproperty`, `mitmattack` so a concrete cipher subclass gets every attack model "for free". |

### Attack model classes (one per attack family)

Each defines a SAT/MILP model builder that takes `start`, `end`, an objective
bound, and returns either a `path`-like trail object or `-1` / `0`.

| File | Class / methods |
| --- | --- |
| [differentialattack.py](differentialattack.py) | `differentialattack` — `diffModel` (single-trail), `diffEffectModel` (path enumeration for differential effect), `impossible` / `impossibleForTruncted` (impossible-differential search), `keyrecoverydist` (r0+r1+r2 differential key recovery). |
| [linearattack.py](linearattack.py) | `linearattack` — `linearModel`, `linearhullModel`, `linear_keyrecoverydist`, `zerocorrelation`. |
| [boomerang.py](boomerang.py) | `boomerang` — `boomerangAttack` (distinguisher) and `boomerangKeyRecovery`. |
| [difflinear.py](difflinear.py) | `difflinear` — `DLAttack`, the differential-linear distinguisher model. |
| [mitm.py](mitm.py) | `mitmattack` — Demirci–Selçuk MITM model (`MITM_Attack`) with `r0 + r1 + r2` split. |
| [divisionproperty.py](divisionproperty.py) | `divisionproperty` — bit-based division-property propagation for integral / zero-sum search (`division(start, end, inpos, outpos)`). |
| [rkdiffattack.py](rkdiffattack.py) | `rkdiffattack` — related-key differential models at multiple granularities: word, bit, fully-bit with 2 permutations, and general permutation×linear matrix `M`. Drives the key-schedule search in `keyschedule/`. |

### Trail / state container

| File | Role |
| --- | --- |
| [path.py](path.py) | All "trail" data classes used by the attack models: `path` (differential/linear), `linear_path`, `keyrecoverypath`, `MITMPath`, `MITMPathKey`, `relatedkeypathW` / `relatedkeypathB` / `relatedkeypathFullBit2P`. Each provides `printPath` (text/LaTeX) and, where applicable, `printAttackFigure` (TikZ figure for the paper). |

### Clean entry points

| File | Role |
| --- | --- |
| [cryptanalysis_clean.py](cryptanalysis_clean.py) | Reviewer-facing inventory + sanity checks. Uses only the standard library plus the vendored `uknit/` reference. Prints the source-file inventory, runs the Section 6 reproduce, checks the four committed test vectors and the embedded S-box/linear-layer constants against the official reference. |
| [SECTION6_MAPPING.md](SECTION6_MAPPING.md) | Human-readable mapping from each Section 6 subsection to the source files that produced its results. |

---

## Sub-directories

Each sub-directory corresponds to one attack family. Pattern: `*.py` driver
scripts (call the model on a concrete cipher) + `run.sh` (sweep of
rounds/objective values) + optional `LATEX/` outputs.

### [`section6/`](section6/) — reviewer reproduction layer

Standard-library-only Section 6 result table and consistency checker.

| File | Role |
| --- | --- |
| [section6/results.py](section6/results.py) | Dataclasses encoding the Section 6 numbers: `AttackSummary`, Table 2 differential / linear bounds, Table 3 related-key bounds, impossible/ZC patterns, integral distinguishers, DS-MITM details, etc. |
| [section6/reproduce.py](section6/reproduce.py) | CLI: prints Tables 1/2/3, the Section 6 mapping, and runs `validate_all()` — checks table shapes, complexity exponents, best-window claims. |
| [section6/__init__.py](section6/__init__.py) | Package marker. |

### [`differential/`](differential/) — Section 6.1 differential trails

| File | Role |
| --- | --- |
| [differential/maindiff.py](differential/maindiff.py) | Sweep driver: for each `(rounds, start)` window and each candidate `obj` (objective = −log₂ probability), call `diffModel` and write a logfile saying feasible / infeasible / timeout. Parallelized with `multiprocessing.Pool(64)`. |
| [differential/run.sh](differential/run.sh) | Sweep schedule: rounds 1..12 with the `obj` ranges to scan (per-round bracket). |

### [`differential_effect/`](differential_effect/) — Section 6.2 differential clustering

Enumerates many trails sharing an input/output difference and clusters their
probabilities (the "differential effect" / DTP analysis).

| File | Role |
| --- | --- |
| [differential_effect/diffeffect.py](differential_effect/diffeffect.py) | Repeatedly calls `diffEffectModel` to find new trails for a single (input,output) difference; accumulates clustered probability for `W(2,8)`. |
| [differential_effect/diffeffectcount.py](differential_effect/diffeffectcount.py) | Same as above but loops over an explicit list of candidate differentials (`Diffs = [...]`, embedded). Used to count distinct (input, output) differences worth clustering. |
| [differential_effect/extract.py](differential_effect/extract.py) | Tiny utility: parse `differentials.txt` lines like `(0,0,...)-...` and return the Python list of difference tuples. Feeds `diffeffectcount.py`. |
| [differential_effect/check.py](differential_effect/check.py) | Spot-check helper: print all S-boxes and push one truncated pattern through a chosen round matrix to verify a hand-derived propagation. |

### [`key-recovery/`](key-recovery/) — differential key recovery (used in 6.1, 6.4, 6.9)

Models the full `r0 + r1 + r2` attack: outer plaintext / ciphertext rounds
(`r0`, `r2`) + middle distinguisher of `r1` rounds.

| File | Role |
| --- | --- |
| [key-recovery/keyrecovery.py](key-recovery/keyrecovery.py) | Linear-layer scratchpad that pushes a chosen ciphertext pattern back through `M^{-1}` to figure out which plaintext nibbles need to be active. Hand-drawn TikZ helpers `printState` / `printFigure`. |
| [key-recovery/keyrecoverydist.py](key-recovery/keyrecoverydist.py) | Single-shot key-recovery solver: calls `keyrecoverydist(start, r0, r1, r2, obj, pro)` on uKNIT-BC, then renders the attack figure as a TikZ/PDF file. |
| [key-recovery/keyrecoverydist_search.py](key-recovery/keyrecoverydist_search.py) | Sweep over `(r0, r1, r2, obj, pro, start)` triples to find the best feasible key-recovery configuration. Multiple commented-out ATTACK arrays record the sweeps we ran for 1+7+2 / 2+7+1 / 3+5+2 / 2+5+3 splits. |

### [`DS-MITM/`](DS-MITM/) — Section 6.7 Demirci–Selçuk MITM

| File | Role |
| --- | --- |
| [DS-MITM/MITM.py](DS-MITM/MITM.py) | Driver: sweep `(OBJ1, OBJ2)` = (online-, offline-complexity bounds), call `MITM_Attack(start, r0, ROUND, r2, ...)`, render successful attacks to LaTeX/PDF. |
| [DS-MITM/checksbox.py](DS-MITM/checksbox.py) | Pushes a chosen anti-diagonal truncated pattern through `M^{-1}` (round 1) to read off which plaintext nibbles are active in the DS-MITM distinguisher. |

### [`linear/`](linear/) — Section 6.3 linear trails

| File | Role |
| --- | --- |
| [linear/linear.py](linear/linear.py) | Sweep driver for `linearModel`. Same shape as `differential/maindiff.py`. |
| [linear/linear_keyrec.py](linear/linear_keyrec.py) | Linear key-recovery sweep `(r0, r1, r2, i, j, z)` calling `linear_keyrecoverydist`. |
| [linear/run.sh](linear/run.sh) | Sweep schedule for `linear.py` over rounds 1..12. |
| [linear/avanzi-tikz-defs.tex](linear/avanzi-tikz-defs.tex) | TikZ macro definitions used by generated linear-trail figures. |

### [`linearhull/`](linearhull/) — Section 6.3 linear hull clustering

| File | Role |
| --- | --- |
| [linearhull/linearhull.py](linearhull/linearhull.py) | One-shot driver that calls `linearhullModel` for a fixed `(INPUT, OUTPUT)` mask pair to enumerate trails inside that hull. |
| [linearhull/linearcount.py](linearhull/linearcount.py) | Same idea but loops over an embedded list `LH = [...]` of candidate linear-hull endpoints to count distinct hulls / accumulate ELP. |
| [linearhull/extract.py](linearhull/extract.py) | Parses `linearhullcount.txt` log file into a Python list. Counterpart of `differential_effect/extract.py`. |

### [`zerocorrelation/`](zerocorrelation/) — Section 6.5 zero-correlation

| File | Role |
| --- | --- |
| [zerocorrelation/zerocorrelation.py](zerocorrelation/zerocorrelation.py) | Sweep over all single-bit input/output positions; calls `linearattack.zerocorrelation`; records UNSAT positions (= zero-correlation hulls). |
| [zerocorrelation/checkmatrix.py](zerocorrelation/checkmatrix.py) | Diagnostic: checks `M·M` and S-box involution-like properties — sanity for the structural arguments. |
| [zerocorrelation/run.sh](zerocorrelation/run.sh) | Sweep schedule (note: file is a leftover copy of `linear/run.sh`). |
| [zerocorrelation/avanzi-tikz-defs.tex](zerocorrelation/avanzi-tikz-defs.tex) | TikZ macros for the generated ZC figures. |

### [`impossible/`](impossible/) — Section 6.4 impossible differential

| File | Role |
| --- | --- |
| [impossible/impossible.py](impossible/impossible.py) | Single-bit impossible-differential sweep: for all `(inpos, outpos)` and starting rounds, call `differentialattack.impossible`; UNSAT means an impossible-differential pattern. |
| [impossible/impossible_check.py](impossible/impossible_check.py) | Verifies one specific truncated impossible-differential pattern via `impossibleForTruncted(3, 10, 61, 0, -1)`. |
| [impossible/idkeyrecovery-1.py](impossible/idkeyrecovery-1.py), [impossible/idkeyrecovery-2.py](impossible/idkeyrecovery-2.py) | Hard-coded `keyrecoverypath` instances (two different active-pattern choices) for the W(1,10) impossible-differential key recovery; render the attack figure as `IDKEY/path.tex` → PDF. |
| [impossible/checksbox.py](impossible/checksbox.py) | Same trick as `DS-MITM/checksbox.py` but with `matrix(10)^{-1}` — used while choosing the ciphertext-side pattern. |

### [`integral/`](integral/) — Section 6.6 integral / division property

| File | Role |
| --- | --- |
| [integral/integral.py](integral/integral.py) | Sweep over all `(inpos, outpos)` single-bit positions; calls `divisionproperty.division`; UNSAT means a zero-sum integral distinguisher. |

### [`Boomerang/`](Boomerang/) — Section 6.8 boomerang / rectangle

| File | Role |
| --- | --- |
| [Boomerang/boom.py](Boomerang/boom.py) | Sweep driver for `boomerangAttack(start, end, middle, obj)`. |
| [Boomerang/boomkey.py](Boomerang/boomkey.py) | Driver for `boomerangKeyRecovery(start, r0, r1, r2, middle, OBJ1, OBJ2)`; renders the 10-round rectangle attack figure to LaTeX/PDF. |

### [`Diff-Linear/`](Diff-Linear/) — Section 6.9 differential-linear

| File | Role |
| --- | --- |
| [Diff-Linear/DL.py](Diff-Linear/DL.py) | Sweep driver for `DLAttack(start, end, middle, obj)` over rounds / middles. |

### [`QuasiDiff/`](QuasiDiff/) — Section 6.1 quasi-differential confirmation

| File | Role |
| --- | --- |
| [QuasiDiff/quasi.py](QuasiDiff/quasi.py) | Independent Gurobi-MILP model: given a fixed differential trail, enumerate compatible *quasi-differential* trails (Beyne, EUROCRYPT 2021) to confirm the trail probability is not an artefact of independence assumptions. Used on W(2,8). |

### [`keyschedule/`](keyschedule/) — related-key search (Section 6 structural arguments)

| File | Role |
| --- | --- |
| [keyschedule/calperm.py](keyschedule/calperm.py) | Helper that combines a nibble permutation `P` with a 16×16 GF(2¹⁶) "diffusion" matrix `A` into one nibble matrix `M = P·A`. Used to generate the candidate key-schedule matrices we feed into the related-key search. |
| [keyschedule/mainM.py](keyschedule/mainM.py) | Sweep driver that calls `rkdiffattack.relatedkeydiff_fullybit_M(M, start, end, obj)` for a chosen `M`. Used to bound related-key differential probabilities. |

### [`Tool/`](Tool/) — small helpers

| File | Role |
| --- | --- |
| [Tool/keyrecoverytool.py](Tool/keyrecoverytool.py) | Given a chosen ciphertext (or plaintext) active-bit pattern, pushes it back two rounds through the inverse / forward matrices to print the implied active-S-box pattern in the previous round. Used to design the key-recovery active patterns by hand. |

---

## Conventions used across the directory

- **State layout.** The 64-bit state is stored as 16 nibbles. Bit / nibble
  conversions are the recurring `GF16to2` and `GF2to16` helpers (4 most-
  significant bit first per nibble). Print order is column-major (`X[0]
  X[4] X[8] X[12]` on the first line) which matches the paper figures.
- **Round counts.** `roundx = 12`, indexed as 12 S-box layers and 11
  linear layers (the last round drops the linear layer).
- **Window notation.** `W(start, end)` means the contiguous slice from round
  `start` (inclusive) to round `end` (exclusive). All sub-directory sweeps
  iterate over `start ∈ [0, 12 - rounds]`.
- **Objective.** In all SAT models, `obj` is the integer −log₂ probability /
  correlation bound being tested; UNSAT at `obj` means no trail with that
  weight exists, SAT means one does.
- **Solver outputs.** Sweep drivers write one `logfile_round{R}_start{S}_obj{O}.txt`
  per task. Generated TikZ files end up under `LATEX/` or `Latex/` and are
  compiled with `pdflatex`.
- **External dependencies.** Top-level attack classes need `numpy` and
  `galois`; `QuasiDiff/quasi.py` needs `gurobipy`. The vendored
  `myutility/` calls the external `kissat` SAT solver and the `espresso`
  logic minimizer at runtime (configurable). The clean entry points
  (`cryptanalysis_clean.py`, `section6/reproduce.py`) deliberately have *no*
  external dependencies beyond the Python standard library.
