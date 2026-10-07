#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse
import hashlib
import math
import random


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        if m <= 0:
            raise ValueError("m must be positive")
        if k <= 0:
            raise ValueError("k must be positive")

        self.m = m
        self.k = k
        self.seed = seed
        self.bits = bytearray((m + 7) // 8)

    def _positions(self, item):
        data = repr(item).encode("utf-8")
        key = self.seed.to_bytes(8, "little", signed=False)

        digest = hashlib.blake2b(
            data,
            digest_size=16,
            key=key
        ).digest()

        h1 = int.from_bytes(digest[:8], "little")
        h2 = int.from_bytes(digest[8:], "little") | 1

        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for pos in self._positions(item):
            byte_index = pos // 8
            bit_index = pos % 8
            self.bits[byte_index] |= 1 << bit_index

    def __contains__(self, item):
        for pos in self._positions(item):
            byte_index = pos // 8
            bit_index = pos % 8

            if not (self.bits[byte_index] & (1 << bit_index)):
                return False

        return True

    def expected_fp_rate(self, n_inserted):
        """The textbook's predicted false-positive rate after n insertions."""
        return (
            1 - math.exp(-self.k * n_inserted / self.m)
        ) ** self.k


def _stable_hash64(item, salt):
    data = repr(item).encode("utf-8")
    key = salt.to_bytes(8, "little", signed=False)

    digest = hashlib.blake2b(
        data,
        digest_size=8,
        key=key
    ).digest()

    return int.from_bytes(digest, "little")


def _trailing_zeros(x):
    if x == 0:
        return 64

    return (x & -x).bit_length() - 1


def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate how many DISTINCT items went past, in almost no memory."""
    if n_hashes <= 0:
        raise ValueError("n_hashes must be positive")

    maxima = [0] * n_hashes

    for item in stream:
        for i in range(n_hashes):
            h = _stable_hash64(item, seed + i)
            r = _trailing_zeros(h)

            if r > maxima[i]:
                maxima[i] = r

    phi = 0.77351

    estimates = sorted(
        (2.0 ** r) / phi
        for r in maxima
    )

    mid = len(estimates) // 2

    if len(estimates) % 2:
        return float(estimates[mid])

    return float(
        (estimates[mid - 1] + estimates[mid]) / 2
    )


def reservoir_sample(stream, k, seed=246):
    """Keep k items uniformly at random from a stream of unknown length."""
    if k <= 0:
        return []

    rng = random.Random(seed)
    reservoir = []

    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = rng.randrange(i + 1)

            if j < k:
                reservoir[j] = item

    return reservoir


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub")
        return 1

    inserted = [f"item-{i}" for i in range(800)]

    for x in inserted:
        bf.add(x)

    check(
        "no false negatives",
        all(x in bf for x in inserted)
    )

    absent = [f"other-{i}" for i in range(20_000)]

    fp = (
        sum(1 for x in absent if x in bf)
        / len(absent)
    )

    predicted = bf.expected_fp_rate(
        len(inserted)
    )

    close = abs(fp - predicted) < max(
        0.02,
        predicted * 0.5
    )

    check(
        "measured false-positive rate matches theory",
        close,
        f"measured {fp:.3%}, predicted {predicted:.3%}"
    )

    # --- Flajolet-Martin
    try:
        distinct = 20_000

        stream = [
            f"k{rng.randrange(distinct)}"
            for _ in range(120_000)
        ]

        est = flajolet_martin(stream)

    except NotImplementedError:
        print("  flajolet_martin is still a stub")
        return 1

    true_distinct = len(set(stream))
    ratio = est / true_distinct

    check(
        "distinct estimate within a factor of 2",
        0.5 <= ratio <= 2.0,
        f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)"
    )

    # --- Reservoir sampling
    try:
        counts = [0] * 20
        trials = 4000

        for t in range(trials):
            s = reservoir_sample(
                range(20),
                5,
                seed=t
            )

            for i in s:
                counts[i] += 1

    except NotImplementedError:
        print("  reservoir_sample is still a stub")
        return 1

    expected = trials * 5 / 20

    spread = (
        max(counts) - min(counts)
    ) / expected

    check(
        "reservoir is uniform across items",
        spread < 0.15,
        f"spread {spread:.1%} around {expected:.0f}"
    )

    print(
        f"\n  "
        f"{'all ok' if not fails else str(fails) + ' failed'}"
    )

    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()

    raise SystemExit(
        verify()
        if a.verify
        else p.print_help()
    )