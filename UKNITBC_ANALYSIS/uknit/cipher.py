"""Pure-Python uKNIT-BC implementation.

The implementation mirrors the reference C++ code in
`uKNIT-implementations-7ABA/uKNIT-BC.cpp` but deliberately uses only the
Python standard library.
"""

from __future__ import annotations

import os
import sys

if __name__ == '__main__' and __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'uknit'

from .constants import (
    INV_LINEAR,
    INV_SBOX,
    KEY_LFSR,
    KEY_PERMUTATION,
    LINEAR,
    LINEAR_LAYER_COUNT,
    ROUND_COUNT,
    SBOX,
    STATE_BITS,
    STATE_NIBBLES,
)


NibbleState = list[int]
MasterKey = tuple[NibbleState, NibbleState]


def _check_nibbles(values: list[int] | tuple[int, ...], *, name: str) -> None:
    if len(values) != STATE_NIBBLES:
        raise ValueError(f"{name} must contain {STATE_NIBBLES} nibbles")
    if any((x < 0 or x > 0xF) for x in values):
        raise ValueError(f"{name} must contain only 4-bit values")


def hex_to_nibbles(value: str) -> NibbleState:
    value = value.strip().lower().removeprefix("0x")
    if len(value) != STATE_NIBBLES:
        raise ValueError(f"expected {STATE_NIBBLES} hexadecimal digits")
    return [int(ch, 16) for ch in value]


def nibbles_to_hex(state: list[int] | tuple[int, ...]) -> str:
    _check_nibbles(state, name="state")
    return "".join(f"{x:x}" for x in state)


def add_round_key(state: list[int] | tuple[int, ...], round_key: list[int] | tuple[int, ...]) -> NibbleState:
    _check_nibbles(state, name="state")
    _check_nibbles(round_key, name="round_key")
    return [x ^ k for x, k in zip(state, round_key)]


def _key_diffusion(key: NibbleState) -> NibbleState:
    key = key[:]
    key[3] = key[0] ^ key[3]
    key[7] = key[4] ^ key[7]
    key[11] = key[8] ^ key[11]
    key[15] = key[12] ^ key[15]
    return key


def _key_permutation(key: NibbleState) -> NibbleState:
    return [key[KEY_PERMUTATION[i]] for i in range(STATE_NIBBLES)]


def _key_lfsr(key: NibbleState) -> NibbleState:
    return [KEY_LFSR[x] for x in key]


def key_schedule(master_key: MasterKey) -> list[NibbleState]:
    """Return the 13 round keys used by uKNIT-BC."""

    if len(master_key) != 2:
        raise ValueError("master_key must be a pair of 16-nibble keys")
    key0 = list(master_key[0])
    key1 = list(master_key[1])
    _check_nibbles(key0, name="master_key[0]")
    _check_nibbles(key1, name="master_key[1]")

    round_keys = [key0[:], key1[:]]
    tmp0 = key0[:]
    tmp1 = key1[:]
    for _ in range(2, ROUND_COUNT + 1):
        tmp0 = _key_permutation(_key_diffusion(tmp0))
        tmp1 = _key_permutation(_key_diffusion(_key_lfsr(tmp1)))
        round_keys.append([a ^ b for a, b in zip(tmp0, tmp1)])
    return round_keys


def substitution_layer(round_index: int, state: list[int] | tuple[int, ...]) -> NibbleState:
    _check_round(round_index, ROUND_COUNT)
    _check_nibbles(state, name="state")
    return [SBOX[round_index][STATE_NIBBLES - 1 - i][x] for i, x in enumerate(state)]


def inv_substitution_layer(round_index: int, state: list[int] | tuple[int, ...]) -> NibbleState:
    _check_round(round_index, ROUND_COUNT)
    _check_nibbles(state, name="state")
    return [INV_SBOX[round_index][STATE_NIBBLES - 1 - i][x] for i, x in enumerate(state)]


def _pack_state(state: list[int] | tuple[int, ...]) -> int:
    value = 0
    for x in state:
        value = (value << 4) ^ x
    return value


def _unpack_state(value: int) -> NibbleState:
    return [(value >> (60 - 4 * i)) & 0xF for i in range(STATE_NIBBLES)]


def _apply_linear(words: list[int], state: list[int] | tuple[int, ...]) -> NibbleState:
    _check_nibbles(state, name="state")
    packed = _pack_state(state)
    result = 0
    for bit_index in range(STATE_BITS):
        if (packed >> (STATE_BITS - 1 - bit_index)) & 1:
            result ^= words[bit_index]
    return _unpack_state(result)


def linear_layer(round_index: int, state: list[int] | tuple[int, ...]) -> NibbleState:
    _check_round(round_index, LINEAR_LAYER_COUNT)
    return _apply_linear(LINEAR[round_index], state)


def inv_linear_layer(round_index: int, state: list[int] | tuple[int, ...]) -> NibbleState:
    _check_round(round_index, LINEAR_LAYER_COUNT)
    return _apply_linear(INV_LINEAR[round_index], state)


def linear_matrix(round_index: int) -> list[list[int]]:
    """Return the 64 x 64 binary matrix with rows as output bits."""

    _check_round(round_index, LINEAR_LAYER_COUNT)
    matrix = [[0 for _ in range(STATE_BITS)] for _ in range(STATE_BITS)]
    for input_bit, word in enumerate(LINEAR[round_index]):
        for output_bit in range(STATE_BITS):
            matrix[output_bit][input_bit] = (word >> (STATE_BITS - 1 - output_bit)) & 1
    return matrix


def encrypt(plaintext: list[int] | tuple[int, ...], master_key: MasterKey) -> NibbleState:
    state = list(plaintext)
    _check_nibbles(state, name="plaintext")
    round_keys = key_schedule(master_key)

    for round_index in range(LINEAR_LAYER_COUNT):
        state = add_round_key(state, round_keys[round_index])
        state = substitution_layer(round_index, state)
        state = linear_layer(round_index, state)

    state = add_round_key(state, round_keys[11])
    state = substitution_layer(11, state)
    return add_round_key(state, round_keys[12])


def decrypt(ciphertext: list[int] | tuple[int, ...], master_key: MasterKey) -> NibbleState:
    state = list(ciphertext)
    _check_nibbles(state, name="ciphertext")
    round_keys = key_schedule(master_key)

    state = add_round_key(state, round_keys[12])
    state = inv_substitution_layer(11, state)
    state = add_round_key(state, round_keys[11])

    for round_index in range(LINEAR_LAYER_COUNT - 1, -1, -1):
        state = inv_linear_layer(round_index, state)
        state = inv_substitution_layer(round_index, state)
        state = add_round_key(state, round_keys[round_index])
    return state


def _check_round(round_index: int, count: int) -> None:
    if round_index < 0 or round_index >= count:
        raise ValueError(f"round_index must be in [0, {count})")
