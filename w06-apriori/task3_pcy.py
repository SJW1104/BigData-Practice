#!/usr/bin/env python3
"""Week 6 · Task 3 — Make pass two fit.

Textbook §6.3 (PCY), §6.3.2 - §6.3.4.

`PlainApriori` does what Task 1 asked: use pass one to drop infrequent items,
then count every pair of surviving items. That is already much better than
counting all pairs. It is still not enough, because the surviving items are the
common ones, and the common ones appear together constantly.

The harness measures **the peak number of pair counters you held**, because
that is the thing that decides whether the algorithm runs at all. §6.3 is about
spending pass one's spare memory to shrink it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: you must find exactly the same frequent pairs. Finding fewer
is not an optimisation.
"""
from collections import Counter
from itertools import combinations


class PlainApriori:
    """Pass one drops infrequent items. Pass two counts every surviving pair."""

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

    def run(self, baskets):
        counts = Counter()

        for basket in baskets:
            counts.update(basket)

        frequent = {
            i for i, c in counts.items()
            if c >= self.support
        }

        pair_counts = Counter()

        for basket in baskets:
            items = sorted(basket & frequent)

            for pair in combinations(items, 2):
                pair_counts[pair] += 1

            self.peak_counters = max(
                self.peak_counters,
                len(pair_counts)
            )

        return {
            frozenset(p): c
            for p, c in pair_counts.items()
            if c >= self.support
        }


class YourAlgorithm:
    """PCY frequent-pair finder.

    Pass 1:
      - count individual items
      - hash every pair into a fixed bucket array

    After pass 1:
      - determine frequent singleton items
      - collapse bucket counts into a bitmap

    Pass 2:
      - only count a pair when both items are frequent
      - and its PCY bucket is frequent
    """

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

        # About one million buckets.
        # Large enough to make the PCY bitmap selective on this dataset,
        # while still being a fixed-size structure.
        self.bucket_count = 1_000_003

    def _bucket(self, pair):
        """Map a pair to one PCY bucket."""
        return hash(pair) % self.bucket_count

    def run(self, baskets):
        # ------------------------------------------------------------
        # PASS 1
        # Count single items and hash every observed pair into buckets.
        # ------------------------------------------------------------
        item_counts = Counter()
        bucket_counts = [0] * self.bucket_count

        for basket in baskets:
            item_counts.update(basket)

            items = sorted(basket)

            for pair in combinations(items, 2):
                bucket = self._bucket(pair)
                bucket_counts[bucket] += 1

        # Frequent singletons from pass one
        frequent_items = {
            item
            for item, count in item_counts.items()
            if count >= self.support
        }

        # ------------------------------------------------------------
        # Collapse bucket counts into a bitmap.
        #
        # A bucket below support cannot contain a frequent pair.
        # bytearray uses one byte per bucket and lets us discard the
        # much larger integer bucket-count array before pass two.
        # ------------------------------------------------------------
        bitmap = bytearray(self.bucket_count)

        for i, count in enumerate(bucket_counts):
            if count >= self.support:
                bitmap[i] = 1

        # Full bucket counts are no longer needed in pass two.
        del bucket_counts

        # ------------------------------------------------------------
        # PASS 2
        # Only count pairs that:
        #   1. contain two frequent singleton items
        #   2. hash to a frequent PCY bucket
        # ------------------------------------------------------------
        pair_counts = Counter()

        for basket in baskets:
            items = sorted(
                item for item in basket
                if item in frequent_items
            )

            for pair in combinations(items, 2):
                bucket = self._bucket(pair)

                if bitmap[bucket]:
                    pair_counts[pair] += 1

            self.peak_counters = max(
                self.peak_counters,
                len(pair_counts)
            )

        # A frequent bucket is only a candidate filter.
        # We still need the real pair count to reach support.
        return {
            frozenset(pair): count
            for pair, count in pair_counts.items()
            if count >= self.support
        }