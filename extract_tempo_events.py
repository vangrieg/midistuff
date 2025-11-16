#!/usr/bin/env python3
"""Extract tempo events from a MIDI file and print them in BPM and time."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import mido
from tempo_to_sysex import build_sysex_message


def prompt_midi_path() -> Path:
    """Prompt the user until an existing MIDI file path is provided."""
    while True:
        try:
            raw = input("Enter path to MIDI file: ").strip()
        except EOFError:
            raise SystemExit("No input provided. Exiting.")

        if not raw:
            print("Path can't be empty. Try again.")
            continue

        path = Path(raw).expanduser()
        if not path.exists():
            print(f"File '{path}' does not exist. Try again.")
            continue

        if not path.is_file():
            print(f"'{path}' is not a file. Try again.")
            continue

        return path


def iter_tempo_events(mid: mido.MidiFile) -> Iterable[tuple[float, float]]:
    """Yield (elapsed_seconds, bpm) for each tempo event in the MIDI file."""
    elapsed_seconds = 0.0
    for message in mid:
        elapsed_seconds += message.time
        if message.type == "set_tempo":
            bpm = mido.tempo2bpm(message.tempo)
            yield elapsed_seconds, bpm


def format_timestamp(seconds: float) -> str:
    """Format seconds as mm.ss.milliseconds."""
    minutes = int(seconds // 60)
    remaining_seconds = seconds - minutes * 60
    sec = int(remaining_seconds)
    milliseconds = int(round((remaining_seconds - sec) * 1000))

    if milliseconds == 1000:
        milliseconds = 0
        sec += 1
        if sec == 60:
            sec = 0
            minutes += 1

    return f"{minutes:02d}:{sec:02d}.{milliseconds:03d}"


def tempo_to_sysex_hex(bpm: float) -> str:
    """Convert a BPM value to a SysEx message string."""
    tempo = int(round(bpm))
    message = build_sysex_message(tempo)
    return " ".join(f"{byte:02X}" for byte in message)


def main() -> None:
    midi_path = prompt_midi_path()
    midi_file = mido.MidiFile(midi_path)

    tempo_events = list(iter_tempo_events(midi_file))
    total_tempo_events = len(tempo_events)

    if not tempo_events:
        print("No tempo events found in the provided MIDI file.")
        print("Tempo events: 0, Output lines: 0 (OK)")
        return

    output_lines = 0
    for elapsed_seconds, bpm in tempo_events:
        timestamp = format_timestamp(elapsed_seconds)
        sysex_hex = tempo_to_sysex_hex(bpm)
        print(f"[midi@{timestamp}: SX{sysex_hex}]")
        output_lines += 1

    status = "OK" if output_lines == total_tempo_events else "MISMATCH"
    print(
        f"Tempo events: {total_tempo_events}, Output lines: {output_lines} ({status})"
    )


if __name__ == "__main__":
    main()
