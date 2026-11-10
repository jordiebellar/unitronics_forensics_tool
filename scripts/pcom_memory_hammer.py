"""
Standalone hotspot verification tool.

Repeatedly reads a small set of known-problematic address ranges from a
V570 PLC and logs every attempt (success or failure) with full frame hex,
so failure patterns can be analyzed statistically instead of relying on
a single occurrence inside a full 16 MB dump.

This does not touch do_read's retry/pad logic - it calls read_binary_frame
and extract_pcom_data directly, once per pass, with retries disabled
(max_retries=1 equivalent), so every single attempt - success or failure -
gets its own log line. This is deliberately different from do_read's
retry-then-pad behavior: for this tool, a "failure" is data, not
something to paper over.

Usage: point HOTSPOTS at the address ranges to hammer, set N_PASSES,
then run this against an already-connected serial port and PCOM_CLIENT
(import from pcom_client.py).
"""

import time
import struct
import datetime
from pcom_client import (
    auto_detect_plc, read_binary_frame, PCOM_CLIENT
)

# Each entry: (start_addr, size_in_bytes, flag, label)
# Sizes here match the exact chunk boundaries identified in the
# 08_27_2026_FLAG_0_BURNED_APP_16MB.bin analysis - reading the whole
# failed span in one shot per pass, not just a single 976-byte slice,
# so a pass either fully succeeds or reproduces the same multi-chunk
# failure pattern seen in the original dump.
HOTSPOTS = [
    (0x000EE0B0, 0x117810 - 0x000EE0B0, 0, "flag0_main_cluster"),
    (0x002C8390, 0x2CBCC0 - 0x002C8390, 0, "flag0_isolated_cluster"),
    (0x00341820, 0x3D0,                 0, "flag0_0x341820_single"),
    (0x00341820, 0x3D0,                 1, "flag1_0x341820_single"),  # same address, other flag
    (0x004F1C00, 0x3D0,                 0, "flag0_0x4F1C00_single"),
]

N_PASSES = 30
READ_CHUNK = 976


def hammer_range(ser, pcom, start_addr, length, flag, label, log_file):
    """
    Read [start_addr, start_addr+length) once, chunked at READ_CHUNK,
    with no retry - every chunk attempt is logged exactly once,
    success or failure, so N_PASSES gives a clean per-address failure
    rate rather than a retry-smoothed one.

    :return: (chunks_attempted, chunks_failed) for this single pass
    """
    addr = start_addr
    remaining = length
    attempted = 0
    failed = 0

    while remaining > 0:
        size = min(READ_CHUNK, remaining)

        read_mem = pcom.create_read_memory(struct.pack("<I", addr), size, flag=flag)
        ser.write(read_mem)
        resp = read_binary_frame(ser, isTcp=pcom.isTcp, out=lambda *a, **k: None)

        chunk = None
        if resp:
            chunk = pcom.extract_pcom_data(resp, expected_payload_len=size, out=lambda *a, **k: None)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        raw_hex = resp.hex() if resp else "(no frame received)"

        if chunk is not None:
            status = "OK"
        else:
            status = "FAIL"
            failed += 1

        log_file.write(
            f"{timestamp}  {status:4s}  region={label}  addr=0x{addr:08X}  size={size}  "
            f"flag={flag}  raw_frame={raw_hex}\n"
        )
        log_file.flush()

        attempted += 1
        addr += size
        remaining -= size

    return attempted, failed


def main():
    result = auto_detect_plc()
    if result is None:
        print("Could not connect to PLC.")
        return
    ser, pcom = result

    log_path = f"hotspot_hammer_{int(time.time())}.txt"
    print(f"[-] Logging to: {log_path}")
    print(f"[-] Running {N_PASSES} passes across {len(HOTSPOTS)} hotspot region(s)...")

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"# Hotspot hammer test - {N_PASSES} passes, {len(HOTSPOTS)} regions\n")
        log_file.write(f"# Started: {datetime.datetime.now().isoformat()}\n\n")

        totals = {label: [0, 0] for _, _, _, label in HOTSPOTS}  # label -> [attempted, failed]

        for pass_num in range(1, N_PASSES + 1):
            print(f"[-] Pass {pass_num}/{N_PASSES}")
            for start_addr, length, flag, label in HOTSPOTS:
                attempted, failed = hammer_range(ser, pcom, start_addr, length, flag, label, log_file)
                totals[label][0] += attempted
                totals[label][1] += failed

        log_file.write("\n# Summary\n")
        for label, (attempted, failed) in totals.items():
            rate = (100 * failed / attempted) if attempted else 0.0
            summary_line = f"# {label}: {failed}/{attempted} chunks failed ({rate:.1f}%)"
            log_file.write(summary_line + "\n")
            print(summary_line)

    ser.close()
    print(f"[-] Done. Full log: {log_path}")


if __name__ == "__main__":
    main()