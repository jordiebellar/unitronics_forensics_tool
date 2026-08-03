"""
diff_memory_maps.py

Compare two memory-map CSVs produced by profile_memory_map() and report,
per offset, whether the probed content changed between the two captures.

Intended use: profile the PLC under two conditions (e.g. app-loaded vs
no-app, or no-app vs no-app-after-reset), then diff the two CSVs to see
exactly which address regions differ and how.

Expected input schema (header row, as written by profile_memory_map):
    offset, offset_hex, entropy, pct_ff, pct_00, md5, first16_hex, ascii_preview

Only `offset` and `md5` are strictly required; entropy/pct_ff/pct_00 are
used to characterize *how* a region changed and are optional.

The MD5 column is the 12-hex-char prefix the profiler writes; both files use
the same truncation, so string comparison of that prefix is the change signal.

    python diff_memory_maps.py map_a.csv map_b.csv
    python diff_memory_maps.py map_no_app.csv map_full_app.csv -o footprint.csv -v
"""

import csv
import os
import sys
import time
import argparse
from collections import Counter

WARNING = "\033[93m"
ENDC = "\033[0m"

# COLUMN SCHEMA

REQUIRED_COLS = ("offset", "md5")
DIFF_COLS = [
    "offset", "offset_hex", "status", "transition",
    "md5_a", "md5_b",
    "entropy_a", "entropy_b", "d_entropy",
    "pct_ff_a", "pct_ff_b", "pct_00_a", "pct_00_b",
]

# HELPERS

def _f(x):
    """
    Parse a float, tolerating empty strings and None.

    :param x: value to parse
    :return: float value, or None if it cannot be parsed
    :rtype: float | None
    """
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _hx(v):
    """
    Format an int address as hex, or pass through non-ints unchanged.

    :param v: address (int) or other value
    :return: hex string like '0x0005c000', else str(v)
    :rtype: str
    """
    return f"0x{v:07x}" if isinstance(v, int) else str(v)


def _mean(vals):
    """
    Mean of the non-None values in an iterable.

    :param vals: iterable of float | None
    :return: mean of the present values, or None if none are present
    :rtype: float | None
    """
    present = [v for v in vals if v is not None]
    return sum(present) / len(present) if present else None


def probe_state(rec: dict) -> str:
    """
    Classify a single probe row by its content.

    :param rec: parsed probe record (offset, md5, pct_ff, pct_00, ...)
    :type rec: dict
    :return: one of 'no-resp', 'FF-fill', '00-fill', 'data'
    :rtype: str
    """
    if not rec.get("md5"):
        return "no-resp"
    ff = rec.get("pct_ff")
    zz = rec.get("pct_00")
    if ff is not None and ff >= 99.5:
        return "FF-fill"
    if zz is not None and zz >= 99.5:
        return "00-fill"
    return "data"


# CSV LOADING

def load_map(path: str, out=print) -> dict:
    """
    Load a memory-map CSV into a dict keyed by integer offset.

    :param path: path to a profile_memory_map CSV
    :type path: str
    :param out: callable used for status/warning output
    :return: mapping of int offset -> parsed record dict
    :rtype: dict[int, dict]
    """
    if not os.path.isfile(path):
        out(f"{WARNING}[X] File not found: {path}{ENDC}")
        sys.exit(1)

    records = {}
    dupes = 0

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            out(f"{WARNING}[X] Empty CSV: {path}{ENDC}")
            sys.exit(1)

        missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing:
            out(f"{WARNING}[X] {path} is missing required column(s): {missing}{ENDC}")
            out(f"    Found columns: {reader.fieldnames}")
            sys.exit(1)

        for line in reader:
            raw_off = (line.get("offset") or "").strip()
            if raw_off == "":
                continue
            try:
                off = int(raw_off, 0)
            except ValueError:
                out(f"{WARNING}[!] Skipping row with bad offset: {raw_off!r}{ENDC}")
                continue

            rec = {
                "offset": off,
                "offset_hex": (line.get("offset_hex") or _hx(off)).strip(),
                "entropy": _f(line.get("entropy")),
                "pct_ff": _f(line.get("pct_ff")),
                "pct_00": _f(line.get("pct_00")),
                "md5": (line.get("md5") or "").strip(),
                "first16_hex": (line.get("first16_hex") or "").strip(),
                "ascii_preview": (line.get("ascii_preview") or "").strip(),
            }
            if off in records:
                dupes += 1
            records[off] = rec  # last write wins

    if dupes:
        out(f"{WARNING}[!] {os.path.basename(path)}: {dupes} duplicate offset(s), kept last.{ENDC}")
    return records


def infer_stride(offsets) -> int:
    """
    Infer the probe stride as the most common gap between sorted offsets.

    :param offsets: sorted iterable of int offsets
    :return: modal positive delta, or 0 if fewer than two offsets
    :rtype: int
    """
    offs = sorted(offsets)
    if len(offs) < 2:
        return 0
    deltas = Counter(b - a for a, b in zip(offs, offs[1:]) if b > a)
    return deltas.most_common(1)[0][0] if deltas else 0


# COMPARISON

def _status_and_transition(ra, rb):
    """
    Determine change status and a transition tag for one offset.

    :param ra: record from map A, or None if absent there
    :param rb: record from map B, or None if absent there
    :return: (status, transition) where status is
             IDENTICAL | CHANGED | ONLY_A | ONLY_B
    :rtype: tuple[str, str]
    """
    sa = probe_state(ra) if ra else "absent"
    sb = probe_state(rb) if rb else "absent"
    transition = f"{sa}->{sb}"

    if ra and rb:
        ma, mb = ra["md5"], rb["md5"]
        if not ma and not mb:
            return "IDENTICAL", transition          # both no-response
        if ma and mb and ma == mb:
            return "IDENTICAL", transition
        return "CHANGED", transition
    if ra and not rb:
        return "ONLY_A", transition
    return "ONLY_B", transition


def compare_maps(a: dict, b: dict) -> list:
    """
    Compare two loaded maps offset-by-offset.

    :param a: map A (int offset -> record)
    :type a: dict
    :param b: map B (int offset -> record)
    :type b: dict
    :return: list of per-offset diff records, sorted by offset
    :rtype: list[dict]
    """
    offsets = sorted(set(a) | set(b))
    diffs = []
    for off in offsets:
        ra, rb = a.get(off), b.get(off)
        status, transition = _status_and_transition(ra, rb)
        ea = ra["entropy"] if ra else None
        eb = rb["entropy"] if rb else None
        diffs.append({
            "offset": off,
            "offset_hex": (ra or rb)["offset_hex"],
            "status": status,
            "transition": transition,
            "md5_a": ra["md5"] if ra else "",
            "md5_b": rb["md5"] if rb else "",
            "entropy_a": ea,
            "entropy_b": eb,
            "d_entropy": (eb - ea) if (ea is not None and eb is not None) else None,
            "pct_ff_a": ra["pct_ff"] if ra else None,
            "pct_ff_b": rb["pct_ff"] if rb else None,
            "pct_00_a": ra["pct_00"] if ra else None,
            "pct_00_b": rb["pct_00"] if rb else None,
            "preview_a": ra["ascii_preview"] if ra else "",
            "preview_b": rb["ascii_preview"] if rb else "",
        })
    return diffs


# REGION CLUSTERING

def cluster_regions(diffs: list, stride: int) -> list:
    """
    Group consecutive same-status probes into contiguous regions.

    A run breaks when the status changes or when the offset gap exceeds the
    stride (i.e. a probe is missing between the two). IDENTICAL runs are
    grouped too, so callers can report coverage, but they are typically
    filtered out of the change report.

    :param diffs: per-offset diff records (sorted by offset)
    :type diffs: list[dict]
    :param stride: probe stride used to detect contiguity
    :type stride: int
    :return: list of region dicts with start/end/count/status/stats
    :rtype: list[dict]
    """
    regions = []
    run = []

    def flush():
        if not run:
            return
        transitions = [d["transition"] for d in run]
        regions.append({
            "start": run[0]["offset"],
            "end": run[-1]["offset"],
            "count": len(run),
            "status": run[0]["status"],
            "transitions": list(dict.fromkeys(transitions)),  # unique, ordered
            "mean_H_a": _mean(d["entropy_a"] for d in run),
            "mean_H_b": _mean(d["entropy_b"] for d in run),
            "mean_ff_a": _mean(d["pct_ff_a"] for d in run),
            "mean_ff_b": _mean(d["pct_ff_b"] for d in run),
            "first": run[0],
        })
        run.clear()

    prev = None
    for d in diffs:
        contiguous = (
            prev is not None
            and d["status"] == prev["status"]
            and stride > 0
            and (d["offset"] - prev["offset"]) == stride
        )
        if not contiguous:
            flush()
        run.append(d)
        prev = d
    flush()
    return regions


# REPORTING

def _fmt_transitions(region):
    """
    Render a region's transition set compactly.

    :param region: region dict from cluster_regions
    :return: single tag, or '{a, b, ...}' when the run is mixed
    :rtype: str
    """
    t = region["transitions"]
    return t[0] if len(t) == 1 else "{" + ", ".join(t) + "}"


def print_report(diffs, regions, stride, label_a, label_b, meta, verbose=False, out=print):
    """
    Print the human-readable diff summary and changed-region table.

    :param diffs: per-offset diff records
    :param regions: clustered regions (all statuses)
    :param stride: inferred probe stride
    :param label_a: display label for map A
    :param label_b: display label for map B
    :param meta: dict with per-map probe counts and offset-set stats
    :param verbose: if True, show per-probe previews for changed regions
    :param out: output callable
    """
    counts = Counter(d["status"] for d in diffs)
    total = len(diffs)

    out("")
    out("=" * 68)
    out(f"[-] A: {label_a}   ({meta['n_a']} probes)")
    out(f"[-] B: {label_b}   ({meta['n_b']} probes)")
    out(f"[-] Compared offsets: {total}   stride: {_hx(stride)}")
    out("=" * 68)
    out(f"    IDENTICAL : {counts.get('IDENTICAL', 0):>6}")
    out(f"    CHANGED   : {counts.get('CHANGED', 0):>6}")
    out(f"    ONLY in A : {counts.get('ONLY_A', 0):>6}")
    out(f"    ONLY in B : {counts.get('ONLY_B', 0):>6}")
    if total:
        pct = 100 * counts.get("IDENTICAL", 0) / total
        out(f"    -> {pct:.1f}% of probed offsets are unchanged")
    if meta["only_a"] or meta["only_b"]:
        out(f"{WARNING}[!] Offset sets differ (A-only={meta['only_a']}, B-only={meta['only_b']}); "
            f"maps may be from different sweeps.{ENDC}")

    changed = [r for r in regions if r["status"] == "CHANGED"]
    only_a = [r for r in regions if r["status"] == "ONLY_A"]
    only_b = [r for r in regions if r["status"] == "ONLY_B"]

    out("")
    if not changed:
        out("[-] No changed regions.")
    else:
        out(f"[-] CHANGED regions ({len(changed)}):")
        out(f"    {'range':<25} {'probes':>6}  {'transition':<22} {'entropy':>14} {'FF%':>13}")
        for r in changed:
            rng = f"{_hx(r['start'])}-{_hx(r['end'])}"
            ha = "--" if r["mean_H_a"] is None else f"{r['mean_H_a']:.2f}"
            hb = "--" if r["mean_H_b"] is None else f"{r['mean_H_b']:.2f}"
            fa = "--" if r["mean_ff_a"] is None else f"{r['mean_ff_a']:.0f}"
            fb = "--" if r["mean_ff_b"] is None else f"{r['mean_ff_b']:.0f}"
            out(f"    {rng:<25} {r['count']:>6}  {_fmt_transitions(r):<22} "
                f"{ha:>6}->{hb:<6} {fa:>5}%->{fb:<4}%")
            if verbose:
                fp = r["first"]
                out(f"        A[{fp['offset_hex']}]: {fp['preview_a']!r}")
                out(f"        B[{fp['offset_hex']}]: {fp['preview_b']!r}")

    for label, group in (("ONLY in A (present in A, absent in B)", only_a),
                         ("ONLY in B (present in B, absent in A)", only_b)):
        if group:
            out("")
            out(f"[-] {label} - {len(group)} region(s):")
            for r in group:
                out(f"    {_hx(r['start'])}-{_hx(r['end'])}  ({r['count']} probes)")


def write_diff_csv(diffs, path, changed_only=False, out=print) -> str:
    """
    Write the full per-offset diff to a CSV.

    :param diffs: per-offset diff records
    :param path: output CSV path
    :param changed_only: if True, write only non-IDENTICAL rows
    :param out: output callable
    :return: the output path
    :rtype: str
    """
    def fnum(v):
        return "" if v is None else f"{v:.3f}"

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(DIFF_COLS)
        for d in diffs:
            if changed_only and d["status"] == "IDENTICAL":
                continue
            writer.writerow([
                d["offset"], d["offset_hex"], d["status"], d["transition"],
                d["md5_a"], d["md5_b"],
                fnum(d["entropy_a"]), fnum(d["entropy_b"]), fnum(d["d_entropy"]),
                fnum(d["pct_ff_a"]), fnum(d["pct_ff_b"]),
                fnum(d["pct_00_a"]), fnum(d["pct_00_b"]),
            ])
    out(f"[-] Saved diff to: {path}")
    return path


# PUBLIC ENTRY

def diff_memory_maps(csv_a, csv_b, output=None, changed_only=False,
                     label_a=None, label_b=None, verbose=False, out=print) -> dict:
    """
    Compare two memory-map CSVs and report the differences.

    :param csv_a: path to the first (baseline) map CSV
    :type csv_a: str
    :param csv_b: path to the second map CSV
    :type csv_b: str
    :param output: path for the diff CSV; auto-named if None
    :type output: str | None
    :param changed_only: write only changed/only rows to the diff CSV
    :type changed_only: bool
    :param label_a: display label for map A (defaults to filename)
    :type label_a: str | None
    :param label_b: display label for map B (defaults to filename)
    :type label_b: str | None
    :param verbose: show per-probe previews for changed regions
    :type verbose: bool
    :param out: output callable
    :return: summary dict with counts, regions, stride, and diff path
    :rtype: dict
    """
    label_a = label_a or os.path.basename(csv_a)
    label_b = label_b or os.path.basename(csv_b)

    a = load_map(csv_a, out=out)
    b = load_map(csv_b, out=out)

    stride = infer_stride(set(a) | set(b))
    diffs = compare_maps(a, b)
    regions = cluster_regions(diffs, stride)

    meta = {
        "n_a": len(a),
        "n_b": len(b),
        "only_a": len(set(a) - set(b)),
        "only_b": len(set(b) - set(a)),
    }

    print_report(diffs, regions, stride, label_a, label_b, meta, verbose=verbose, out=out)

    if output is None:
        base_a = os.path.splitext(os.path.basename(csv_a))[0]
        base_b = os.path.splitext(os.path.basename(csv_b))[0]
        output = f"diff_{base_a}_vs_{base_b}_{int(time.time())}.csv"
    diff_path = write_diff_csv(diffs, output, changed_only=changed_only, out=out)

    counts = Counter(d["status"] for d in diffs)
    return {
        "counts": dict(counts),
        "regions": regions,
        "stride": stride,
        "diff_csv": diff_path,
        "meta": meta,
    }


def main() -> None:
    """
    CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Diff two memory-map CSVs produced by profile_memory_map().")
    parser.add_argument("csv_a", help="baseline map CSV (A)")
    parser.add_argument("csv_b", help="comparison map CSV (B)")
    parser.add_argument("-o", "--output", default=None,
                        help="diff CSV output path (auto-named if omitted)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="show ASCII previews for each changed region")
    parser.add_argument("--changed-only", action="store_true",
                        help="write only changed/only-in rows to the diff CSV")
    parser.add_argument("--label-a", default=None, help="display label for A")
    parser.add_argument("--label-b", default=None, help="display label for B")
    args = parser.parse_args()

    diff_memory_maps(
        args.csv_a, args.csv_b,
        output=args.output,
        changed_only=args.changed_only,
        label_a=args.label_a,
        label_b=args.label_b,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()