"""
compare_dumps.py — diff two PCOM operand dump folders.

Usage:
    python compare_dumps.py <baseline_folder> <capture_folder>

Output:
    diff_summary.txt   one line per operand type with change count
    diff_detail.csv    every changed address with before/after values
"""

import sys, csv, os
from pathlib import Path

OPERAND_FILES = [
    ("MB",  "mb_dump.csv",  "bit"),
    ("MI",  "mi_dump.csv",  "int16"),
    ("ML",  "ml_dump.csv",  "int32"),
    ("MDW", "mdw_dump.csv", "uint32"),
    ("MF",  "mf_dump.csv",  "float"),
    ("SB",  "sb_dump.csv",  "bit"),
    ("SI",  "si_dump.csv",  "int16"),
    ("SL",  "sl_dump.csv",  "int32"),
    ("SDW", "sdw_dump.csv", "uint32"),
]

def load_csv(path: Path) -> dict:
    """Load a dump CSV into {address: value} dict."""
    result = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result[int(row["address"])] = row["value"]
    return result

def delta(a, b, dtype: str) -> str:
    """Compute numeric delta where possible."""
    try:
        fa = float(a)
        fb = float(b)
        d = fb - fa
        if dtype == "float":
            return f"{d:.6f}"
        return str(int(d))
    except ValueError:
        return ""

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_dumps.py <baseline_folder> <capture_folder>")
        sys.exit(1)

    baseline_dir = Path(sys.argv[1])
    capture_dir  = Path(sys.argv[2])

    summary_lines = []
    detail_rows = []

    for label, fname, dtype in OPERAND_FILES:
        b_path = baseline_dir / fname
        c_path = capture_dir  / fname

        if not b_path.exists() or not c_path.exists():
            summary_lines.append(f"{label:>4s}  SKIPPED (file missing)")
            continue

        baseline = load_csv(b_path)
        capture  = load_csv(c_path)

        all_addrs = sorted(set(baseline) | set(capture))
        changes = 0

        for addr in all_addrs:
            bval = baseline.get(addr, "MISSING")
            cval = capture.get(addr,  "MISSING")
            if bval != cval:
                changes += 1
                d = delta(bval, cval, dtype) if bval != "MISSING" and cval != "MISSING" else ""
                detail_rows.append({
                    "operand_type": label,
                    "address":      addr,
                    "baseline":     bval,
                    "capture":      cval,
                    "delta":        d,
                })

        summary_lines.append(f"{label:>4s}  {changes:>6d} changes  ({len(all_addrs)} addresses compared)")

    # Write summary
    with open("diff_summary.txt", "w") as f:
        f.write(f"Baseline: {baseline_dir}\n")
        f.write(f"Capture:  {capture_dir}\n\n")
        f.write("\n".join(summary_lines))
    print("[-] Wrote diff_summary.txt")

    # Write detail CSV
    with open("diff_detail.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["operand_type","address","baseline","capture","delta"])
        writer.writeheader()
        writer.writerows(detail_rows)
    print(f"[-] Wrote diff_detail.csv ({len(detail_rows)} changed addresses)")

if __name__ == "__main__":
    main()