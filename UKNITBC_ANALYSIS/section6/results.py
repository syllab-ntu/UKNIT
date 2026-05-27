"""Structured Section 6 cryptanalysis results for uKNIT-BC.

This module is intentionally standard-library only.  The historical search
scripts live alongside this file; here we record the Section 6 results in a
form that can be checked, printed, and mapped back to those scripts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AttackSummary:
    name: str
    rounds: int
    target_window: str
    time_log2: float
    data_log2: float
    section: str


@dataclass(frozen=True)
class SectionEntry:
    section: str
    title: str
    legacy_scripts: tuple[str, ...]
    result_summary: str
    reproducible_result: str
    external_search_requirements: tuple[str, ...] = ()


@dataclass(frozen=True)
class RelatedKeyEntry:
    value: int
    lower_bound: bool = False

    def label(self) -> str:
        return f">={self.value}" if self.lower_bound else str(self.value)


DIFFERENTIAL_BOUNDS = {
    1: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    2: [8, 8, 6, 6, 8, 8, 6, 8, 8, 6, 8],
    3: [14, 12, 12, 12, 14, 14, 12, 14, 12, 12],
    4: [25, 23, 24, 26, 30, 26, 26, 24, 24],
    5: [40, 40, 39, 40, 40, 39, 37, 37],
    6: [49, 48, 46, 46, 50, 47, 49],
    7: [60, 58, 52, 61, 60, 59],
    8: [71, 70, 68, 71, 72],
    9: [81, 82, 80, 82],
    10: [94, 87, 92],
    11: [101, 99],
    12: [113],
}


LINEAR_BOUNDS = {
    1: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    2: [4, 4, 3, 3, 4, 4, 3, 4, 4, 3, 4],
    3: [7, 6, 6, 6, 7, 6, 6, 7, 6, 6],
    4: [13, 10, 11, 13, 14, 12, 12, 11, 12],
    5: [19, 18, 19, 19, 19, 18, 17, 17],
    6: [24, 23, 22, 23, 25, 23, 21],
    7: [29, 26, 26, 30, 29, 27],
    8: [35, 34, 34, 34, 34],
    9: [39, 38, 37, 39],
    10: [45, 44, 43],
    11: [49, 50],
    12: [55],
}


RELATED_KEY_DIFFERENTIAL_BOUNDS = {
    1: [RelatedKeyEntry(0) for _ in range(12)],
    2: [RelatedKeyEntry(0) for _ in range(11)],
    3: [RelatedKeyEntry(2) for _ in range(10)],
    4: [RelatedKeyEntry(v) for v in [6, 7, 6, 6, 6, 6, 6, 6, 6]],
    5: [RelatedKeyEntry(v) for v in [14, 12, 14, 12, 11, 13, 13, 13]],
    6: [RelatedKeyEntry(v) for v in [25, 21, 22, 24, 19, 23, 22]],
    7: [RelatedKeyEntry(v, True) for v in [29, 29, 29, 30, 30, 31]],
    8: [RelatedKeyEntry(v, True) for v in [32, 33, 33, 32, 33]],
    9: [RelatedKeyEntry(v, True) for v in [35, 35, 35, 35]],
    10: [RelatedKeyEntry(v, True) for v in [41, 42, 41]],
    11: [RelatedKeyEntry(v, True) for v in [45, 45]],
    12: [RelatedKeyEntry(49, True)],
}


MAIN_KEY_RECOVERY_ATTACKS = (
    AttackSummary("Differential", 10, "W(0, 10)", 110.0, 55.7, "6.1"),
    AttackSummary("Impossible differential", 10, "W(1, 10)", 93.0, 55.0, "6.4"),
    AttackSummary("Demirci-Selcuk MITM", 9, "W(0, 9)", 87.0, 61.0, "6.7"),
    AttackSummary("Differential-linear", 9, "W(1, 9)", 92.6, 53.6, "6.9"),
)


IMPOSSIBLE_AND_ZC_PATTERNS = (
    {
        "window": "W(3, 7)",
        "input": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        "output": (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    },
    {
        "window": "W(3, 7)",
        "input": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        "output": (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    },
)


INTEGRAL_DISTINGUISHERS = (
    {"window": "W(3, 7)", "input_bits": (60, 61, 62, 63), "output_bits": (0, 1, 2, 3)},
    {"window": "W(3, 7)", "input_bits": (60, 61, 62, 63), "output_bits": (12, 13, 14, 15)},
)


DETAILS = {
    "6.1": {
        "differential_attack": {
            "target_window": "W(0, 10)",
            "distinguisher_window": "W(2, 7)",
            "distinguisher_probability_log2": 53.0,
            "backward_rounds": 2,
            "forward_rounds": 1,
            "structure_size_log2": 48.0,
            "structure_count_log2": 7.7,
            "data_log2": 55.7,
            "time_log2": 110.0,
        },
        "quasi_differential_check": {
            "window": "W(2, 8)",
            "probability_log2": 68.0,
            "nonzero_mask_trails": 0,
            "all_zero_mask_trail": True,
        },
    },
    "6.2": {
        "multiple_differential": {
            "window": "W(2, 8)",
            "searched_characteristics": 100,
            "characteristic_probability_log2": 68.0,
            "distinct_differentials": 72,
            "truncated_patterns": 3,
            "best_differential_probability_log2": 63.3,
        },
    },
    "6.3": {
        "linear_key_recovery_candidate": {
            "target_window": "W(0, 10)",
            "distinguisher_window": "W(2, 7)",
            "correlation_log2": 30.0,
            "backward_key_bits": 96,
            "forward_key_bits": 24,
        },
        "linear_hull": {
            "window": "W(2, 8)",
            "searched_characteristics": 100,
            "characteristic_correlation_log2": 34.0,
            "linear_truncated_patterns": 7,
            "best_elp_log2": 62.4,
            "input_mask": (0, 0, 0, 0, 0xB, 4, 0, 0xE, 0, 0, 0, 0, 0, 0, 0, 0),
            "output_mask": (0, 2, 0, 4, 2, 0, 2, 0, 0, 0, 0, 1, 8, 0, 0, 0),
        },
    },
    "6.4": {
        "key_recovery": {
            "target_window": "W(1, 10)",
            "distinguisher_window": "W(3, 7)",
            "data_log2": 55.0,
            "pair_count_log2": 69.0,
            "passing_keys_per_pair_log2": 24.0,
            "time_log2": 93.0,
            "memory_blocks_log2": 86.0,
        },
    },
    "6.5": {
        "zero_correlation": {
            "window": "W(3, 7)",
            "same_patterns_as_impossible_differentials": True,
        },
    },
    "6.6": {
        "integral": {
            "longest_zero_sum_rounds": 7,
            "no_zero_sum_for_all_8_round_windows": True,
            "no_one_sum_for_8_round_windows_with_keys": True,
        },
    },
    "6.7": {
        "ds_mitm": {
            "target_window": "W(0, 9)",
            "distinguisher_window": "W(2, 5)",
            "data_log2": 61.0,
            "memory_blocks_log2": 34.0,
            "offline_time_5_round_log2": 40.0,
            "online_time_4_round_log2": 88.0,
            "time_9_round_log2": 87.0,
        },
    },
    "6.8": {
        "rectangle": {
            "best_8_round": {"window": "W(1, 8)", "probability_log2": 141.0},
            "best_7_round": {"window": "W(2, 7)", "probability_log2": 116.0},
        },
    },
    "6.9": {
        "differential_linear": {
            "target_window": "W(1, 9)",
            "distinguisher_window": "W(2, 7)",
            "detected_correlation_log2": 25.0,
            "experimental_correlation_log2": 23.0,
            "advantage_log2": 54.0,
            "pair_count_log2": 52.6,
            "data_log2": 53.6,
            "time_log2": 92.6,
        },
        "best_8_round_distinguisher": {
            "window": "W(3, 8)",
            "detected_correlation_log2": 35.0,
            "experimental_correlation_log2": 31.83,
        },
    },
    "6.10": {
        "invariant": {
            "search_script_required": False,
            "reason": "Structural argument based on nontrivial key schedule.",
        },
    },
    "6.11": {
        "slide_internal": {
            "search_script_required": False,
            "reason": "Structural argument based on non-aligned round functions.",
        },
    },
}


SECTION_ENTRIES = (
    SectionEntry(
        "6.1",
        "Simple differential cryptanalysis",
        (
            "differential/maindiff.py",
            "key-recovery/keyrecoverydist.py",
            "key-recovery/keyrecoverydist_search.py",
            "differentialattack.py",
            "QuasiDiff/quasi.py",
        ),
        "Table 2 differential bounds; 10-round W(0,10) attack with time 2^110 and data 2^55.7.",
        "Differential table, quasi-differential fact, and key-recovery complexity.",
        ("SAT solver", "Gurobi for quasi-differential search", "LaTeX for old figures"),
    ),
    SectionEntry(
        "6.2",
        "Multiple differential cryptanalysis",
        ("differential_effect/diffeffect.py", "differential_effect/diffeffectcount.py", "differential_effect/extract.py"),
        "100 characteristics over W(2,8), 72 differentials, 3 DTPs, best differential about 2^-63.3.",
        "Multiple-differential clustering result.",
        ("SAT solver",),
    ),
    SectionEntry(
        "6.3",
        "Linear and linear-hull cryptanalysis",
        ("linear/linear.py", "linear/linear_keyrec.py", "linearhull/linearhull.py", "linearhull/linearcount.py", "linearattack.py"),
        "Table 2 linear bounds; W(2,8) best ELP about 2^-62.4.",
        "Linear table and linear-hull summary.",
        ("SAT solver",),
    ),
    SectionEntry(
        "6.4",
        "Impossible differential cryptanalysis",
        ("impossible/impossible.py", "impossible/impossible_check.py", "impossible/idkeyrecovery-1.py", "impossible/idkeyrecovery-2.py", "differentialattack.py"),
        "Two W(3,7) impossible truncated differentials; 10-round W(1,10) attack with time 2^93 and data 2^55.",
        "Impossible patterns and key-recovery complexity.",
        ("SAT solver", "LaTeX for old figures"),
    ),
    SectionEntry(
        "6.5",
        "Zero-correlation cryptanalysis",
        ("zerocorrelation/zerocorrelation.py", "zerocorrelation/checkmatrix.py", "linearattack.py"),
        "Two W(3,7) zero-correlation hulls matching the impossible-differential patterns.",
        "Zero-correlation pattern summary.",
        ("SAT solver",),
    ),
    SectionEntry(
        "6.6",
        "Integral attacks",
        ("integral/integral.py", "divisionproperty.py"),
        "Longest zero-sum property is 7 rounds; no W(i,8) zero-sum or key-aware one-sum property found.",
        "Integral distinguisher summary.",
        ("SAT solver",),
    ),
    SectionEntry(
        "6.7",
        "Demirci-Selcuk meet-in-the-middle attack",
        ("DS-MITM/MITM.py", "DS-MITM/checksbox.py", "mitm.py"),
        "9-round W(0,9) DS-MITM attack with time about 2^87, data 2^61, memory 2^34 blocks.",
        "DS-MITM complexity summary.",
        ("SAT solver", "LaTeX for old figures"),
    ),
    SectionEntry(
        "6.8",
        "Boomerang and rectangle attacks",
        ("Boomerang/boom.py", "Boomerang/boomkey.py", "boomerang.py"),
        "Best 8-round rectangle estimate is 2^-141; best 7-round estimate is 2^-116.",
        "Rectangle distinguisher summary.",
        ("SAT solver", "LaTeX for old figures"),
    ),
    SectionEntry(
        "6.9",
        "Differential-linear attacks",
        ("Diff-Linear/DL.py", "difflinear.py"),
        "9-round W(1,9) attack with time 2^92.6 and data 2^53.6; best 8-round DL distinguisher is not threatening.",
        "Differential-linear distinguisher and key-recovery complexity.",
        ("SAT solver",),
    ),
    SectionEntry(
        "6.10",
        "Invariant attack",
        (),
        "No dedicated search script; security argument is structural.",
        "Recorded as a no-code structural argument.",
    ),
    SectionEntry(
        "6.11",
        "Slide and internal differential attacks",
        (),
        "No dedicated search script; security argument is structural.",
        "Recorded as a no-code structural argument.",
    ),
)
