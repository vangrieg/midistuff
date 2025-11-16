#!/usr/bin/env python3
"""List MIDI output devices and send a user-specified SysEx message."""

from __future__ import annotations

import sys
from typing import Iterable

import mido


def list_output_ports() -> list[str]:
    """Return available MIDI output port names."""
    try:
        return mido.get_output_names()
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Mido requires the 'python-rtmidi' package for MIDI output. "
            "Install it and try again."
        ) from exc
    except (IOError, OSError) as exc:
        raise RuntimeError(f"Unable to enumerate MIDI outputs: {exc}") from exc


def prompt_port_choice(ports: list[str]) -> str:
    """Prompt the user to choose a port from the provided list."""
    while True:
        print("Available MIDI output ports:")
        for index, name in enumerate(ports, start=1):
            print(f"  {index}: {name}")

        try:
            raw = input("Select output port by number: ").strip()
        except EOFError:
            raise SystemExit("No input provided. Exiting.")

        if not raw:
            print("Selection cannot be empty. Try again.")
            continue

        if not raw.isdigit():
            print("Please enter a numeric selection.")
            continue

        choice = int(raw)
        if not (1 <= choice <= len(ports)):
            print("Selection out of range. Try again.")
            continue

        return ports[choice - 1]


def parse_sysex_input(raw_message: str) -> list[int]:
    """Parse a textual SysEx message into a list of integer bytes."""
    sanitized = raw_message.replace(",", " ")
    tokens = sanitized.split()

    # Allow inputs without whitespace by falling back to pairs
    if len(tokens) <= 1:
        stripped = sanitized.replace(" ", "")
        if len(stripped) % 2 != 0:
            raise ValueError("SysEx message must have an even number of hex digits.")
        tokens = [stripped[i : i + 2] for i in range(0, len(stripped), 2)]

    bytes_out: list[int] = []
    for token in tokens:
        token = token.lower()
        if token.startswith("0x"):
            token = token[2:]
        if not token:
            raise ValueError("Empty token in SysEx message.")
        value = int(token, 16)
        if not 0 <= value <= 0xFF:
            raise ValueError(f"SysEx byte '{token}' is out of range 00-FF.")
        bytes_out.append(value)

    if not bytes_out:
        raise ValueError("SysEx message cannot be empty.")

    return bytes_out


def prompt_sysex_message() -> list[int]:
    """Prompt the user for a SysEx message and return it as integer bytes."""
    while True:
        try:
            raw = input(
                "Enter SysEx message bytes (hex, e.g. 'F0 00 01 74 11 14 78 00 6A F7'): "
            ).strip()
        except EOFError:
            raise SystemExit("No input provided. Exiting.")

        if not raw:
            print("SysEx message cannot be empty. Try again.")
            continue

        try:
            message = parse_sysex_input(raw)
        except ValueError as exc:
            print(f"Invalid SysEx message: {exc}")
            continue

        return message


def prepare_sysex_payload(bytes_in: Iterable[int]) -> list[int]:
    """Normalize SysEx bytes for mido by stripping F0/F7 if present."""
    data = list(bytes_in)

    if data[0] == 0xF0:
        data = data[1:]
    if data and data[-1] == 0xF7:
        data = data[:-1]

    return data


def send_sysex(port_name: str, sysex_bytes: list[int]) -> None:
    """Send the SysEx message to the specified output port."""
    payload = prepare_sysex_payload(sysex_bytes)
    if not payload:
        raise ValueError("SysEx payload is empty after removing F0/F7 markers.")

    message = mido.Message("sysex", data=payload)
    with mido.open_output(port_name) as port:
        port.send(message)


def main() -> None:
    try:
        ports = list_output_ports()
    except RuntimeError as exc:
        print(exc)
        sys.exit(1)
    if not ports:
        print("No MIDI output ports available.")
        sys.exit(1)

    port_name = prompt_port_choice(ports)
    sysex_bytes = prompt_sysex_message()

    try:
        send_sysex(port_name, sysex_bytes)
    except (IOError, OSError) as exc:
        print(f"Failed to open '{port_name}': {exc}")
        sys.exit(1)
    except ValueError as exc:
        print(f"Cannot send SysEx: {exc}")
        sys.exit(1)

    hex_repr = " ".join(f"{byte:02X}" for byte in sysex_bytes)
    print(f"Sent SysEx to '{port_name}': {hex_repr}")


if __name__ == "__main__":
    main()
