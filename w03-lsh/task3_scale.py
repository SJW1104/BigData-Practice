#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.
"""

import random


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()

        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))

        return out


class YourFinder:
    """MinHash + LSH near-duplicate finder."""

    PRIME = 2305843009213693951

    def __init__(self, threshold):
        self.threshold = threshold

        # 120 hashes = 30 bands * 4 rows.
        #
        # Approximate S-curve step:
        # (1 / 30)^(1 / 4) ≈ 0.427
        #
        # The assignment threshold is 0.6, so the step is intentionally below
        # it. This favors recall: pairs near 0.6 have a high chance of becoming
        # candidates, while exact similarity() is still called only on the
        # candidate set.
        self.num_hashes = 120
        self.bands = 30
        self.rows_per_band = 4

        rng = random.Random(202603)

        self.a = [
            rng.randrange(1, self.PRIME)
            for _ in range(self.num_hashes)
        ]

        self.b = [
            rng.randrange(0, self.PRIME)
            for _ in range(self.num_hashes)
        ]

    def _to_int(self, value):
        """Convert a shingle into a stable integer."""
        if isinstance(value, int):
            return value % self.PRIME

        data = str(value).encode("utf-8")

        # Deterministic 64-bit FNV-1a hash.
        h = 1469598103934665603

        for byte in data:
            h ^= byte
            h *= 1099511628211
            h &= (1 << 64) - 1

        return h % self.PRIME

    def _signature(self, doc):
        """Create one MinHash signature."""
        if not doc:
            return [self.PRIME] * self.num_hashes

        values = [self._to_int(x) for x in doc]
        signature = [self.PRIME] * self.num_hashes

        for x in values:
            for k in range(self.num_hashes):
                hashed = (self.a[k] * x + self.b[k]) % self.PRIME

                if hashed < signature[k]:
                    signature[k] = hashed

        return signature

    def find(self, docs, similarity):
        """Return near-duplicate pairs using MinHash + LSH."""
        if len(docs) < 2:
            return set()

        signatures = [
            self._signature(doc)
            for doc in docs
        ]

        candidates = set()

        for band in range(self.bands):
            start = band * self.rows_per_band
            end = start + self.rows_per_band
            buckets = {}

            for doc_id, signature in enumerate(signatures):
                key = tuple(signature[start:end])
                buckets.setdefault(key, []).append(doc_id)

            for bucket in buckets.values():
                for i in range(len(bucket)):
                    for j in range(i + 1, len(bucket)):
                        candidates.add((bucket[i], bucket[j]))

        out = set()

        for i, j in candidates:
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))

        return out
