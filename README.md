# MIDI Utilities

A small collection of Python helpers for working with MIDI tempo data.

## Setup

Install dependencies with pip:

```bash
python3 -m pip install -r requirements.txt
```

## Scripts

### `tempo_to_sysex.py`

Prompts for a tempo (10–255 BPM), converts it into a Roland-style SysEx message, and prints the full byte sequence including checksum.

Run it directly:

```bash
python3 tempo_to_sysex.py
```

### `extract_tempo_events.py`

Prompts for the path to a MIDI file and emits each tempo change in the format `BPM:MM:SS.mmm`.

Run it directly:

```bash
python3 extract_tempo_events.py
```

When prompted, provide the path to a MIDI file containing tempo meta events.

### `send_sysex.py`

Discovers available MIDI output devices, lets you choose one, prompts for a SysEx message in hex, and sends it to the selected port.

Run it directly:

```bash
python3 send_sysex.py
```

Enter the port number and the SysEx message (e.g. `F0 00 01 74 11 14 78 00 6A F7`) when prompted.
