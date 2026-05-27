#!/usr/bin/env python3
"""Clean entry point for the uKNIT-BC cryptanalysis code.

This directory contains the research scripts used to generate SAT/MILP-style
models and experiment artifacts for uKNIT-BC.  This file provides a small,
reviewer-friendly map of those scripts plus deterministic sanity checks that
require only the Python standard library.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PKG_ROOT = Path(__file__).resolve().parent

sys.path.insert(0, str(PKG_ROOT))

from uknit.cipher import decrypt, encrypt, hex_to_nibbles, nibbles_to_hex  # noqa: E402
from uknit.model_compat import compare_uknit_bc_model  # noqa: E402

from section6.reproduce import (  # noqa: E402
    print_mapping as print_section6_mapping,
    print_summary as print_section6_summary,
    validate_all as validate_section6,
)


ATTACK_GROUPS = [
    {
        "name": "Section 6 reproduction",
        "paper_topic": "Reviewer-facing mapping and checks for all Section 6 claims",
        "files": [
            "SECTION6_MAPPING.md",
            "section6/__init__.py",
            "section6/results.py",
            "section6/reproduce.py",
        ],
        "notes": "Standard-library result table, source mapping, and consistency checker.",
    },
    {
        "name": "Cipher model",
        "paper_topic": "uKNIT-BC round function used by all attacks",
        "files": [
            "uknit_bc.py",
            "newcipher.py",
            "path.py",
        ],
        "notes": "uknit_bc.py is checked against the official reference constants.",
    },
    {
        "name": "Differential cryptanalysis",
        "paper_topic": "Differential trails and differential key recovery",
        "files": [
            "differentialattack.py",
            "differential/maindiff.py",
            "key-recovery/keyrecovery.py",
            "key-recovery/keyrecoverydist.py",
            "key-recovery/keyrecoverydist_search.py",
        ],
        "notes": "Legacy scripts build SAT constraints and previously generated trail/key-recovery logs.",
    },
    {
        "name": "Linear cryptanalysis",
        "paper_topic": "Linear trails, linear hull, and linear key recovery",
        "files": [
            "linearattack.py",
            "linear/linear.py",
            "linear/linear_keyrec.py",
            "linearhull/linearhull.py",
            "linearhull/linearcount.py",
            "linearhull/extract.py",
        ],
        "notes": "Ignored SAT/log outputs were removed; source scripts remain.",
    },
    {
        "name": "Boomerang and rectangle",
        "paper_topic": "Boomerang/rectangle distinguishers and key recovery",
        "files": [
            "boomerang.py",
            "Boomerang/boom.py",
            "Boomerang/boomkey.py",
        ],
        "notes": "LaTeX render outputs were removed; source and remaining TeX descriptions remain.",
    },
    {
        "name": "Differential-linear",
        "paper_topic": "Differential-linear distinguishers",
        "files": [
            "difflinear.py",
            "Diff-Linear/DL.py",
        ],
        "notes": "Generated SAT directories were removed.",
    },
    {
        "name": "Impossible and zero-correlation",
        "paper_topic": "Impossible differential and zero-correlation searches",
        "files": [
            "impossible/impossible.py",
            "impossible/impossible_check.py",
            "impossible/idkeyrecovery-1.py",
            "impossible/idkeyrecovery-2.py",
            "zerocorrelation/zerocorrelation.py",
            "zerocorrelation/checkmatrix.py",
        ],
        "notes": "Search scripts rely on the historical SAT utility layer.",
    },
    {
        "name": "Integral and division property",
        "paper_topic": "Integral/division-property analysis",
        "files": [
            "divisionproperty.py",
            "integral/integral.py",
        ],
        "notes": "The deterministic cipher-model checks are in the bundled uknit/ package.",
    },
    {
        "name": "Meet-in-the-middle",
        "paper_topic": "DS-MITM and MITM searches",
        "files": [
            "mitm.py",
            "DS-MITM/MITM.py",
            "DS-MITM/checksbox.py",
        ],
        "notes": "Historical LaTeX/PDF outputs were removed.",
    },
    {
        "name": "Related-key and key schedule",
        "paper_topic": "Related-key differential modeling",
        "files": [
            "rkdiffattack.py",
            "keyschedule/calperm.py",
            "keyschedule/mainM.py",
        ],
        "notes": "These scripts still depend on external solver/math utilities.",
    },
]


TEST_VECTORS = [
    ("0000000000000000", "0000000000000000", "0000000000000000", "034af0b3c687e424"),
    ("0123456789abcdef", "0123456789abcdef", "0123456789abcdef", "7d4ef882c1f42dba"),
    ("ffffffffffffffff", "ffffffffffffffff", "ffffffffffffffff", "db058583df8f186f"),
    ("1111111111111111", "fedcba9876543210", "0123456789abcdef", "7c8ddaf0fead3409"),
]


def missing_files() -> list[str]:
    missing = []
    for group in ATTACK_GROUPS:
        for relative in group["files"]:
            if not (PKG_ROOT / relative).exists():
                missing.append(relative)
    return missing


def check_cipher_model() -> dict[str, object]:
    return compare_uknit_bc_model(PKG_ROOT / "uknit_bc.py")


def check_reference_vectors() -> list[str]:
    failures = []
    for plaintext, key0, key1, expected in TEST_VECTORS:
        master_key = (hex_to_nibbles(key0), hex_to_nibbles(key1))
        ciphertext = encrypt(hex_to_nibbles(plaintext), master_key)
        got = nibbles_to_hex(ciphertext)
        if got != expected:
            failures.append(f"encrypt({plaintext}) = {got}, expected {expected}")
        recovered = decrypt(ciphertext, master_key)
        if nibbles_to_hex(recovered) != plaintext:
            failures.append(f"decrypt({expected}) = {nibbles_to_hex(recovered)}, expected {plaintext}")
    return failures


def run_checks() -> int:
    missing = missing_files()
    model = check_cipher_model()
    vector_failures = check_reference_vectors()
    section6_errors = validate_section6()

    print("uKNIT-BC cryptanalysis sanity checks")
    print("=" * 40)
    print(f"Attack source groups: {len(ATTACK_GROUPS)}")
    print(f"Missing listed source files: {missing}")
    print(f"uKNIT-BC model entries: {model['model_entries']}")
    print(f"S-box mismatches: {model['sbox_mismatches']}")
    print(f"linear-layer mismatches: {model['linear_mismatches']}")
    print(f"test-vector failures: {vector_failures}")
    print(f"Section 6 result mismatches: {section6_errors}")

    ok = (
        not missing
        and not model["sbox_mismatches"]
        and not model["linear_mismatches"]
        and not vector_failures
        and not section6_errors
    )
    print("status: OK" if ok else "status: FAILED")
    return 0 if ok else 1


def print_inventory() -> None:
    print("uKNIT-BC cryptanalysis source inventory")
    print("=" * 40)
    for group in ATTACK_GROUPS:
        print(f"\n[{group['name']}]")
        print(f"paper topic: {group['paper_topic']}")
        print(f"notes: {group['notes']}")
        for relative in group["files"]:
            marker = "ok" if (PKG_ROOT / relative).exists() else "missing"
            print(f"  - {relative} ({marker})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run deterministic standard-library checks")
    parser.add_argument("--inventory", action="store_true", help="print the attack source inventory")
    parser.add_argument("--section6", action="store_true", help="print the Section 6 result summary and source mapping")
    args = parser.parse_args(argv)

    if not args.check and not args.inventory and not args.section6:
        args.check = True
        args.inventory = True
        args.section6 = True

    status = 0
    printed = False
    if args.inventory:
        print_inventory()
        printed = True
    if args.section6:
        if printed:
            print()
        print_section6_summary()
        print()
        print_section6_mapping()
        printed = True
    if args.check:
        if printed:
            print()
        status = run_checks()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
