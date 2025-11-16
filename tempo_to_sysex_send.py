#!/usr/bin/env python3
"""Prompt for a tempo, build the SysEx message, and send it to a MIDI port."""

from __future__ import annotations

import sys

from tempo_to_sysex import build_sysex_message, read_tempo
from send_sysex import list_output_ports, prompt_port_choice, send_sysex


def main() -> None:
    try:
        ports = list_output_ports()
    except RuntimeError as exc:
        print(exc)
        sys.exit(1)

    if not ports:
        print("No MIDI output ports available.")
        sys.exit(1)

    tempo = read_tempo()
    message = build_sysex_message(tempo)
    hex_repr = " ".join(f"{byte:02X}" for byte in message)
    print(f"Tempo {tempo} -> SysEx message: {hex_repr}")

    port_name = prompt_port_choice(ports)

    try:
        send_sysex(port_name, message)
    except (IOError, OSError) as exc:
        print(f"Failed to open '{port_name}': {exc}")
        sys.exit(1)
    except ValueError as exc:
        print(f"Cannot send SysEx: {exc}")
        sys.exit(1)

    print(f"Sent SysEx to '{port_name}'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        sys.exit(1)
