"""
locate_mi_in_raw_memory.py

Writes a set of distinct, easily-fingerprinted values into MI (memory
integer) operands, confirms each one via read-back through the normal
operand path (the layer you've already proven works), then takes a raw
memory dump of the application flag and searches it byte-for-byte for
each value's encoding.

Point of this: instead of inferring where things live in the raw 16 MB
address space by diffing two whole ladder logic programs (HELLO_WORLD vs
CURVES), you get ground truth. You know exactly what you wrote and to
which MI address, so any place it shows up in the raw dump is a verified
data point for an operand-to-physical-address map, not a guess.

Only touches memory through the confirmed-working write path (ASCII
SW / write_memory_integers). Never calls create_write_memory (the raw
byte-address write, opcode 0x41) - that path is separately established
as rejected on this unit and this script doesn't need it.

Usage: run standalone against an already-reachable V570.
"""

import struct
import datetime
from pcom_client import (
    auto_detect_plc, do_read, write_and_verify_memory_integers
)

# --- Configuration -----------------------------------------------------

# MI addresses to write to, and the distinct value to put in each one.
# Values are chosen to be unlikely to occur naturally in memory (not 0,
# not a small round number, not a power of two) so a hit in the raw dump
# is a meaningful signal rather than coincidence. Spread across low,
# mid, and higher MI indices in case the operand table isn't stored
# contiguously with a simple linear offset.
MI_TEST_VALUES = {
    0:  12345,
    1:  23456,
    2: -1234,      # negative, to also confirm two's-complement encoding
    10: 30001,
    50: 30051,
}

DUMP_FLAG = 1            # 1 = application memory (the safe, working flag).
                          # Do NOT set this to 0 (OS/firmware) for this experiment.
DUMP_START = 0x0
DUMP_END = 0x1000000     # 16 MB. Narrow this once a rough region turns up -
                          # a full sweep is slow (~17k chunked reads).
DUMP_READ_SIZE = 976
DUMP_LOG_PATH = None      # set a path if you want do_read's retry/failure log


def encode_candidates(value: int) -> dict[str, bytes]:
    """
    Every byte encoding worth searching for. ASCII PCOM sends MI as a
    4-hex-digit (16-bit) value on the wire, but the underlying flash/RAM
    representation - width, endianness, whether it's word-aligned inside
    a wider slot - is exactly what this experiment is trying to establish,
    so don't assume just one.
    """
    v16 = value & 0xFFFF
    return {
        "u16_le": struct.pack("<H", v16),
        "u16_be": struct.pack(">H", v16),
        "u32_le": struct.pack("<I", v16),   # in case MI sits in a 32-bit slot
        "u32_be": struct.pack(">I", v16),
    }


def search_dump(dump: bytes, value: int) -> dict[str, list[int]]:
    """Return {encoding_name: [offsets]} for every place `value` appears."""
    hits = {}
    for name, pattern in encode_candidates(value).items():
        offsets = []
        start = 0
        while True:
            idx = dump.find(pattern, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
        if offsets:
            hits[name] = offsets
    return hits


def offset_is_padded(offset: int, failed_ranges: list[tuple[int, int]]) -> bool:
    return any(fa <= offset < fa + fs for fa, fs in failed_ranges)


def main():
    result = auto_detect_plc()
    if result is None:
        print("[X] Could not connect to PLC.")
        return
    ser, pcom = result

    try:
        # --- Step 1: write + verify each MI value one at a time --------
        print(f"[-] Writing and verifying {len(MI_TEST_VALUES)} distinct MI value(s)...")
        for addr, value in MI_TEST_VALUES.items():
            results = write_and_verify_memory_integers(ser, pcom, start=addr, values=[value])
            if results is None or not results.get(addr, False):
                print(f"[X] MI{addr} did not verify on read-back. Stopping before the dump - "
                      f"searching for a value that was never actually confirmed written "
                      f"would just manufacture false positives.")
                return

        # --- Step 2: raw dump of application memory ----------------------
        print(f"\n[-] All values verified. Dumping flag={DUMP_FLAG} from "
              f"{hex(DUMP_START)} to {hex(DUMP_END)} ({DUMP_END - DUMP_START} bytes)...")
        dump, failed_ranges = do_read(
            ser, pcom, addr=DUMP_START, length=DUMP_END - DUMP_START,
            flag=DUMP_FLAG, read_size=DUMP_READ_SIZE, log_path=DUMP_LOG_PATH,
        )

        dump_name = f"mi_locate_dump_flag{DUMP_FLAG}_{int(datetime.datetime.now().timestamp())}.bin"
        with open(dump_name, "wb") as f:
            f.write(dump)
        print(f"[-] Dump saved to {dump_name} ({len(dump)} bytes, "
              f"{len(failed_ranges)} unread chunk(s) padded with 0xAA)")

        # --- Step 3: search the dump for each written value ---------------
        print("\n[-] Searching dump for each written value...\n")
        for addr, value in MI_TEST_VALUES.items():
            hits = search_dump(dump, value)
            if not hits:
                print(f"MI{addr} = {value}: no match found anywhere in this flag/range.")
                continue
            for encoding, offsets in hits.items():
                real_offsets = [o for o in offsets if not offset_is_padded(o, failed_ranges)]
                padded_count = len(offsets) - len(real_offsets)
                note = f"  ({padded_count} more inside padded/unread chunks, ignored)" if padded_count else ""
                if len(real_offsets) == 1:
                    print(f"MI{addr} = {value}  [{encoding}]  -> unique hit at "
                          f"0x{real_offsets[0]:08X}{note}")
                elif real_offsets:
                    shown = ", ".join(f"0x{o:08X}" for o in real_offsets[:10])
                    more = " ..." if len(real_offsets) > 10 else ""
                    print(f"MI{addr} = {value}  [{encoding}]  -> {len(real_offsets)} hits, "
                          f"not unique on its own - treat as noise unless the SAME offset "
                          f"recurs for a different value written to a different address "
                          f"(that would mean this encoding/width guess is wrong, not that "
                          f"MI isn't there): {shown}{more}{note}")

        print("\n[-] Done. A unique hit that lands at a plausible, consistent offset "
              "across more than one MI address (e.g. MI1's hit is exactly 2 bytes past "
              "MI0's) is your confirmation of both the base address and the per-operand "
              "stride - that's the actual mapping you're after.")

    finally:
        ser.close()


if __name__ == "__main__":
    main()
