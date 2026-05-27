"""Compatibility checks against the bundled `uknit_bc.py` model."""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

if __name__ == '__main__' and __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'uknit'

from .constants import LINEAR, LINEAR_LAYER_COUNT, SBOX, STATE_BITS, STATE_NIBBLES
from .cipher import linear_matrix


def load_uknit_bc_model(path: str | Path) -> list:
    """Load the `UKNIT_BC_MODEL` literal without importing legacy dependencies."""

    source = Path(path).read_text()
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "UKNIT_BC_MODEL":
                    return ast.literal_eval(node.value)
    raise ValueError(f"UKNIT_BC_MODEL assignment not found in {path}")


def model_sbox(model: list, round_index: int, sbox_index: int) -> list[int]:
    return model[2 * round_index][STATE_NIBBLES - 1 - sbox_index]


def model_matrix(model: list, round_index: int) -> list[list[int]]:
    sparse = model[2 * round_index + 1]
    matrix = [[0 for _ in range(STATE_BITS)] for _ in range(STATE_BITS)]
    for source_bit in range(STATE_BITS):
        for layer in sparse:
            if layer[source_bit] != -1:
                matrix[STATE_BITS - 1 - source_bit][STATE_BITS - 1 - layer[source_bit]] = 1
    return matrix


def words_from_matrix(matrix: list[list[int]]) -> list[int]:
    words = []
    for input_bit in range(STATE_BITS):
        word = 0
        for output_bit in range(STATE_BITS):
            if matrix[output_bit][input_bit]:
                word |= 1 << (STATE_BITS - 1 - output_bit)
        words.append(word)
    return words


def compare_uknit_bc_model(path: str | Path) -> dict[str, object]:
    model = load_uknit_bc_model(path)
    sbox_mismatches = []
    for round_index in range(12):
        if model[2 * round_index] != SBOX[round_index]:
            sbox_mismatches.append(round_index)
        for sbox_index in range(STATE_NIBBLES):
            if model_sbox(model, round_index, sbox_index) != SBOX[round_index][15 - sbox_index]:
                sbox_mismatches.append((round_index, sbox_index))

    linear_mismatches = []
    for round_index in range(LINEAR_LAYER_COUNT):
        matrix = model_matrix(model, round_index)
        if matrix != linear_matrix(round_index):
            linear_mismatches.append(round_index)
        if words_from_matrix(matrix) != LINEAR[round_index]:
            linear_mismatches.append(("words", round_index))

    return {
        "sbox_mismatches": sbox_mismatches,
        "linear_mismatches": linear_mismatches,
        "model_entries": len(model),
    }
