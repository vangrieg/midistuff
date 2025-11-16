#!/usr/bin/env python3
"""Prompt for a tempo and print the corresponding SysEx message."""

from __future__ import annotations

from functools import reduce
from typing import Sequence

MIN_TEMPO = 10
MAX_TEMPO = 255


def read_tempo() -> int:
    """Prompt the user until a valid tempo integer is entered."""
    while True:
        try:
            raw = input(f"Enter tempo ({MIN_TEMPO}-{MAX_TEMPO}): ").strip()
        except EOFError:
            raise SystemExit("No input provided. Exiting.")

        if not raw:
            print("Tempo can't be empty. Try again.")
            continue

        try:
            tempo = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if not (MIN_TEMPO <= tempo <= MAX_TEMPO):
            print(f"Tempo must be between {MIN_TEMPO} and {MAX_TEMPO}.")
            continue

        return tempo


def tempo_to_sysex_bytes(tempo: int) -> tuple[int, int]:
    """Convert tempo to a two-byte little-endian tuple suitable for SysEx."""
    lsb = tempo & 0x7F
    msb = (tempo >> 7) & 0x7F
    return lsb, msb


def calculate_checksum(data: Sequence[int]) -> int:
    """Calculate the 7-bit XOR checksum for the provided data bytes."""
    if not data:
        raise ValueError("Checksum requires at least one byte of data.")

    xor_result = reduce(lambda x, y: x ^ y, data)
    return xor_result & 0x7F


def build_sysex_message(tempo: int) -> list[int]:
    """Build the SysEx message for the given tempo, including checksum."""
    lsb, msb = tempo_to_sysex_bytes(tempo)
    body = [0xF0, 0x00, 0x01, 0x74, 0x11, 0x14, lsb, msb]
    checksum = calculate_checksum(body)
    return body + [checksum, 0xF7]


def main() -> None:
    tempo = read_tempo()
    message = build_sysex_message(tempo)
    hex_message = " ".join(f"{byte:02X}" for byte in message)
    print(f"Tempo {tempo} -> SysEx message: {hex_message}")


if __name__ == "__main__":
    main()
