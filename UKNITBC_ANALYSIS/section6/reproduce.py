#!/usr/bin/env python3
"""Print and check the Section 6 cryptanalysis results for uKNIT-BC."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from section6.results import (  # type: ignore
        DETAILS,
        DIFFERENTIAL_BOUNDS,
        IMPOSSIBLE_AND_ZC_PATTERNS,
        INTEGRAL_DISTINGUISHERS,
        LINEAR_BOUNDS,
        MAIN_KEY_RECOVERY_ATTACKS,
        RELATED_KEY_DIFFERENTIAL_BOUNDS,
        SECTION_ENTRIES,
    )
else:
    from .results import (
        DETAILS,
        DIFFERENTIAL_BOUNDS,
        IMPOSSIBLE_AND_ZC_PATTERNS,
        INTEGRAL_DISTINGUISHERS,
        LINEAR_BOUNDS,
        MAIN_KEY_RECOVERY_ATTACKS,
        RELATED_KEY_DIFFERENTIAL_BOUNDS,
        SECTION_ENTRIES,
    )


def fmt_log2(value: float | int) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")


def fmt_power(value: float | int) -> str:
    return f"2^{fmt_log2(value)}"


def table_rows(table: dict[int, list[object]]) -> list[str]:
    rows = []
    for rounds in sorted(table):
        values = []
        for item in table[rounds]:
            label = item.label() if hasattr(item, "label") else str(item)
            values.append(label)
        rows.append(f"r={rounds:2d}: " + " ".join(f"{value:>4}" for value in values))
    return rows


def minimum_entry(table: dict[int, list[int]], rounds: int) -> tuple[int, int]:
    values = table[rounds]
    best = min(values)
    return values.index(best), best


def print_table(name: str) -> None:
    if name == "differential":
        print("Table 2 left: differential probabilities (-log2)")
        print("\n".join(table_rows(DIFFERENTIAL_BOUNDS)))
    elif name == "linear":
        print("Table 2 right: linear correlations (-log2)")
        print("\n".join(table_rows(LINEAR_BOUNDS)))
    elif name == "related-key":
        print("Table 3: related-key differential probabilities (-log2)")
        print("\n".join(table_rows(RELATED_KEY_DIFFERENTIAL_BOUNDS)))
    elif name == "attacks":
        print("Table 1: main key-recovery attacks")
        for attack in MAIN_KEY_RECOVERY_ATTACKS:
            print(
                f"{attack.section:>4} | {attack.name:<25} | {attack.rounds:2d} rounds | "
                f"{attack.target_window:<8} | time {fmt_power(attack.time_log2):<8} | "
                f"data {fmt_power(attack.data_log2)}"
            )
    else:
        raise ValueError(f"unknown table: {name}")


def print_mapping() -> None:
    print("Section 6 mapping")
    print("=" * 72)
    for entry in SECTION_ENTRIES:
        scripts = ", ".join(entry.legacy_scripts) if entry.legacy_scripts else "none"
        reqs = ", ".join(entry.external_search_requirements) if entry.external_search_requirements else "none"
        print(f"{entry.section} {entry.title}")
        print(f"  legacy scripts: {scripts}")
        print(f"  reproducible result: {entry.reproducible_result}")
        print(f"  legacy full-search extras (not needed here): {reqs}")
        print(f"  result: {entry.result_summary}")


def print_summary() -> None:
    print("uKNIT-BC Section 6 cryptanalysis results")
    print("=" * 72)
    print_table("attacks")
    print()
    diff_start, diff_value = minimum_entry(DIFFERENTIAL_BOUNDS, 8)
    lin_start, lin_value = minimum_entry(LINEAR_BOUNDS, 8)
    print(f"Best 8-round differential table entry: W({diff_start}, 8) with probability {fmt_power(-diff_value)}")
    print(f"Best 8-round linear table entry: W({lin_start}, 8) with correlation {fmt_power(-lin_value)}")
    print(f"Multiple differential W(2,8): best clustered probability about {fmt_power(-DETAILS['6.2']['multiple_differential']['best_differential_probability_log2'])}")
    print(f"Linear hull W(2,8): best ELP about {fmt_power(-DETAILS['6.3']['linear_hull']['best_elp_log2'])}")
    print(f"Rectangle best 8-round estimate: {fmt_power(-DETAILS['6.8']['rectangle']['best_8_round']['probability_log2'])}")
    print(f"DL 9-round key recovery: time {fmt_power(DETAILS['6.9']['differential_linear']['time_log2'])}, data {fmt_power(DETAILS['6.9']['differential_linear']['data_log2'])}")


def validate_table_shapes(errors: list[str]) -> None:
    for name, table in (
        ("differential", DIFFERENTIAL_BOUNDS),
        ("linear", LINEAR_BOUNDS),
        ("related-key", RELATED_KEY_DIFFERENTIAL_BOUNDS),
    ):
        for rounds in range(1, 13):
            expected = 13 - rounds
            got = len(table[rounds])
            if got != expected:
                errors.append(f"{name} r={rounds}: expected {expected} windows, got {got}")


def validate_main_attacks(errors: list[str]) -> None:
    expected = {
        "Differential": ("W(0, 10)", 110.0, 55.7),
        "Impossible differential": ("W(1, 10)", 93.0, 55.0),
        "Demirci-Selcuk MITM": ("W(0, 9)", 87.0, 61.0),
        "Differential-linear": ("W(1, 9)", 92.6, 53.6),
    }
    for attack in MAIN_KEY_RECOVERY_ATTACKS:
        target, time_log2, data_log2 = expected[attack.name]
        if (attack.target_window, attack.time_log2, attack.data_log2) != (target, time_log2, data_log2):
            errors.append(f"main attack mismatch for {attack.name}")


def validate_complexities(errors: list[str]) -> None:
    diff = DETAILS["6.1"]["differential_attack"]
    if round(diff["structure_size_log2"] + diff["structure_count_log2"], 1) != diff["data_log2"]:
        errors.append("6.1 differential data exponent mismatch")

    impossible = DETAILS["6.4"]["key_recovery"]
    if impossible["pair_count_log2"] + impossible["passing_keys_per_pair_log2"] != impossible["time_log2"]:
        errors.append("6.4 impossible differential time exponent mismatch")

    ds = DETAILS["6.7"]["ds_mitm"]
    if ds["online_time_4_round_log2"] - 1 != ds["time_9_round_log2"]:
        errors.append("6.7 DS-MITM round-normalized time mismatch")

    dl = DETAILS["6.9"]["differential_linear"]
    structure_count = dl["pair_count_log2"] - 39.0
    data = structure_count + 40.0
    online = 40.0 + 39.0 + structure_count
    exhaustive = 128.0 - dl["advantage_log2"]
    time = max(data, online, exhaustive)
    if round(data, 1) != dl["data_log2"] or round(time, 1) != dl["time_log2"]:
        errors.append("6.9 differential-linear complexity mismatch")


def validate_claims(errors: list[str]) -> None:
    diff_start, diff_value = minimum_entry(DIFFERENTIAL_BOUNDS, 8)
    if (diff_start, diff_value) != (2, 68):
        errors.append("best 8-round differential entry should be W(2,8) with exponent 68")

    lin_start, lin_value = minimum_entry(LINEAR_BOUNDS, 8)
    if (lin_start, lin_value) != (1, 34):
        errors.append("best 8-round linear entry should include exponent 34")

    if DETAILS["6.2"]["multiple_differential"]["distinct_differentials"] != 72:
        errors.append("6.2 distinct differential count mismatch")
    if DETAILS["6.3"]["linear_hull"]["linear_truncated_patterns"] != 7:
        errors.append("6.3 LTP count mismatch")
    if len(IMPOSSIBLE_AND_ZC_PATTERNS) != 2:
        errors.append("6.4/6.5 should list two patterns")
    if len(INTEGRAL_DISTINGUISHERS) != 2:
        errors.append("6.6 should list two integral distinguishers derived from ZC")


def validate_all() -> list[str]:
    errors: list[str] = []
    validate_table_shapes(errors)
    validate_main_attacks(errors)
    validate_complexities(errors)
    validate_claims(errors)
    return errors


def run_check() -> int:
    errors = validate_all()
    if errors:
        print("Section 6 result check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Section 6 result check: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="print the main Section 6 result summary")
    parser.add_argument("--mapping", action="store_true", help="print the Section 6 to source-file mapping")
    parser.add_argument("--check", action="store_true", help="check internal consistency of recorded results")
    parser.add_argument(
        "--table",
        choices=("attacks", "differential", "linear", "related-key"),
        action="append",
        default=[],
        help="print a specific Section 6 table",
    )
    args = parser.parse_args(argv)

    if not args.summary and not args.mapping and not args.check and not args.table:
        args.summary = True
        args.mapping = True
        args.check = True

    if args.summary:
        print_summary()
    if args.mapping:
        if args.summary:
            print()
        print_mapping()
    for table in args.table:
        if args.summary or args.mapping:
            print()
        print_table(table)

    status = 0
    if args.check:
        if args.summary or args.mapping or args.table:
            print()
        status = run_check()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
