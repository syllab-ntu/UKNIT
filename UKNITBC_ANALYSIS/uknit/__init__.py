"""Standalone uKNIT-BC implementation used by the reviewer artifact."""

import os
import sys

if __name__ == '__main__' and __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'uknit'

from .cipher import (
    add_round_key,
    decrypt,
    encrypt,
    hex_to_nibbles,
    inv_linear_layer,
    inv_substitution_layer,
    key_schedule,
    linear_layer,
    linear_matrix,
    nibbles_to_hex,
    substitution_layer,
)

__all__ = [
    "add_round_key",
    "decrypt",
    "encrypt",
    "hex_to_nibbles",
    "inv_linear_layer",
    "inv_substitution_layer",
    "key_schedule",
    "linear_layer",
    "linear_matrix",
    "nibbles_to_hex",
    "substitution_layer",
]
