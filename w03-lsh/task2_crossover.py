#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4.

This version keeps the original timing loop, but generates exactly the requested
number of synthetic documents so sizes above 2,120 are real measurements.
"""
import argparse
import json
import os
import platform
import random
import time
import tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    info = {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
    }

    # Best-effort RAM detection on Windows.
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info["ram_gb"] = round(status.ullTotalPhys / (1024 ** 3), 1)
    except Exception:
        pass

    return info


def timed(fn, *args):
    """Wall time and peak memory of one call."""
    tracemalloc.start()
    t0 = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak


def build_docs(n, bench, seed=246):
    """Build exactly n synthetic documents with bench-like characteristics.

    The original bench.build() always returns 2,120 documents. Task 2 asks us
    to keep raising n beyond that, so this generator preserves the same shingle
    size, vocabulary and approximate near-duplicate ratio while producing the
    exact requested size.
    """
    rng = random.Random(seed + n)

    # Keep roughly the same ratio as bench.py:
    # 2,000 base documents + 120 planted near-duplicates.
    clone_ratio = bench.PLANTED / (bench.N_DOCS + bench.PLANTED)
    n_clones = int(round(n * clone_ratio))
    n_base = max(1, n - n_clones)

    docs = [
        set(rng.sample(range(bench.VOCAB), bench.SHINGLES))
        for _ in range(n_base)
    ]

    for _ in range(n_clones):
        source = rng.randrange(n_base)
        clone = set(docs[source])

        for _ in range(rng.randint(4, 14)):
            if clone:
                clone.discard(rng.choice(tuple(clone)))
            clone.add(rng.randrange(bench.VOCAB))

        docs.append(clone)

    rng.shuffle(docs)
    return docs


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--sizes",
        default="250,500,1000,2000",
        help="comma-separated document counts to try",
    )
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument(
        "--reset",
        action="store_true",
        help="clear previous crossover.json measurements before this run",
    )
    a = p.parse_args()

    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_scale import BruteForce

    try:
        from task3_scale import YourFinder
    except Exception:
        YourFinder = None

    path = os.path.join(OUT, "crossover.json")

    if a.reset and os.path.exists(path):
        os.remove(path)

    rows = []

    for n in [int(x.strip()) for x in a.sizes.split(",") if x.strip()]:
        docs = build_docs(n, bench)

        sim = bench.Counter()
        _, t_brute, m_brute = timed(
            BruteForce(a.threshold).find, docs, sim
        )
        c_brute = sim.calls

        row = {
            "n": len(docs),
            "brute_s": t_brute,
            "brute_calls": c_brute,
            "brute_peak_bytes": m_brute,
        }

        if YourFinder is not None:
            sim2 = bench.Counter()

            try:
                _, t_lsh, m_lsh = timed(
                    YourFinder(a.threshold).find, docs, sim2
                )
                row.update({
                    "lsh_s": t_lsh,
                    "lsh_calls": sim2.calls,
                    "lsh_peak_bytes": m_lsh,
                })
            except NotImplementedError:
                pass

        rows.append(row)

        line = (
            f"  n={len(docs):>6}  "
            f"brute {t_brute:>8.2f}s  {c_brute:>12,} cmp"
        )

        if "lsh_s" in row:
            line += (
                f"   |  lsh {row['lsh_s']:>7.2f}s  "
                f"{row['lsh_calls']:>9,} cmp"
            )

        print(line)

    prior = (
        json.load(open(path, encoding="utf-8"))
        if os.path.exists(path)
        else {"runs": []}
    )

    prior["machine"] = machine()
    prior["runs"].extend(rows)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(prior, f, indent=2)

    print(
        f"\n  -> out/crossover.json  "
        f"({len(prior['runs'])} measurement(s))"
    )
    print(
        "  Keep raising --sizes until something becomes unpleasant. "
        "Record where."
    )


if __name__ == "__main__":
    main()
