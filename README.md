# Unitronics PCOM Forensics Toolkit

A from-scratch reverse-engineered client for Unitronics' proprietary PCOM protocol, built to extract forensic evidence from Vision/Samba series PLCs (V570 and related models) over serial and TCP.

This grew out of the 2023–2024 Unitronics attacks against water treatment and other critical infrastructure sites (CVE-2024-38434), where publicly documented tooling was limited to the two utilities Claroty's Team82 released (PCOM2TCP and PCOMClient). This project independently re-implements and extends that capability: full binary and ASCII PCOM framing, read/write across all nine operand types, signature-table extraction for post-incident attribution, and a sparse entropy-based memory profiler for characterizing the full 16 MB address space without a full dump.

The tooling here is the foundation for an ongoing MS thesis in PLC forensics (Unitronics V570 memory/firmware analysis) — this repo covers the protocol layer; deeper binary forensic work (bank replication mapping, region classification, string extraction) builds on top of it.

## Features

**Protocol layer (`pcom_client.py`)**
- Full PCOM binary and ASCII packet construction/parsing, including CRC calculation for both binary header/footer and ASCII framing
- TCP and serial transport (auto-wraps binary packets with the 6-byte TCP header when `isTcp=True`)
- Auto-detection: scans all available serial ports across five baud rates (115200 down to 9600) and confirms a live PLC via a read-name probe before locking in
- Read/write support for all nine operand types: MB, MI, ML, MDW, MF (memory bits/ints/longs/dwords/floats) and SB, SI, SL, SDW (system equivalents)
- PLC identification: name, firmware/version table (OS, boot, factory boot, BinLib), unit ID, upload/auth password check
- Signature table extraction and parsing — decompresses the zlib-framed metadata blob and recovers project name and other embedded fields, the same forensic artifact Team82's research identified as carrying attacker/engineer attribution data
- Project ZIP read-back (resource ID 6) for pulling the full VisiLogic project off a live PLC
- Sparse memory profiler (`profile_memory_map`): probes at a configurable stride across up to 16 MB, recording Shannon entropy, %0xFF, %0x00, MD5, and an ASCII preview per probe — enough to characterize the whole address space in a few hundred round trips instead of a full dump, and to surface mirrored content (e.g. the app image replicated across flash banks) via repeated MD5s
- Bulk CSV export of every operand type in one pass (`dump_all_csv`)
- STOP command support (guarded — see Safety notes below)

**GUI (`pcom_gui.py`)**
- FreeSimpleGUI front-end over the same client: PLC info buttons, one-click CSV/ZIP/memory-dump saves with native save dialogs, live scrolling log, and a confirmation prompt before sending STOP

**Analysis scripts**
- `compare_dumps.py` — diffs two `dump_all_csv` folders operand-by-operand, computing numeric deltas per address and writing a summary + detailed CSV
- `compare_memory_profiles.py` — diffs two memory-map CSVs from the profiler, classifies each offset as IDENTICAL/CHANGED/ONLY_A/ONLY_B, clusters contiguous changed regions, and reports entropy/fill-byte deltas per region — built for exactly the "app-loaded vs no-app" or "before vs after reset" comparisons a forensic timeline needs

- ## Repo structure

```
.
├── compare_dumps.py             # diff two dump_all_csv folders (operand-level)
├── compare_memory_profiles.py   # diff two memory-map CSVs (entropy/region-level)
└── PCOM_CLIENT/
    ├── pcom_client.py           # protocol implementation + CLI menu (main entry point)
    └── pcom_gui.py              # FreeSimpleGUI front-end over pcom_client
```

## Requirements

- Python 3.10+ (uses `X | Y` union type hints throughout)
- [`pyserial`](https://pypi.org/project/pyserial/) — required by `pcom_client.py`
- [`FreeSimpleGUI`](https://pypi.org/project/FreeSimpleGUI/) — required only by `pcom_gui.py`

```bash
pip install pyserial FreeSimpleGUI
```

## Usage

**CLI (recommended starting point):**

```bash
cd PCOM_CLIENT
python pcom_client.py
```

On launch, it scans every available serial port at 115200 → 9600 baud looking for a PLC that responds to a read-name request, authenticates with the default upload password, then drops into a numbered menu (PLC name/firmware/unit ID, signature table, project ZIP read, memory dump, full CSV dump, memory-map profiling, STOP, etc.).

**GUI:**

```bash
cd PCOM_CLIENT
python pcom_gui.py
```

Same underlying operations behind buttons, with native save dialogs for CSV/ZIP/binary dump output and a scrolling log pane.

**Comparing two captures:**

```bash
# operand-level diff (from two dump_all_csv folders)
python compare_dumps.py baseline_folder/ capture_folder/

# region-level diff (from two profile_memory_map CSVs)
python compare_memory_profiles.py map_a.csv map_b.csv -v --changed-only
```
