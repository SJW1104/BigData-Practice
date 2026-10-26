#!/usr/bin/env python3
"""Week 6 · Task 4 (optional) — SON: A-Priori that survives being split up.

Textbook §6.4.3 (the SON algorithm) and §6.4.4 (SON and MapReduce).

Tasks 1 and 3 both assume the baskets fit on one machine. SON does not. It is
the textbook's own answer to "what if they do not", it is two passes, and it has
a guarantee that most sampling schemes do not:

    an itemset that is frequent overall is frequent in at least one chunk

which is why pass one can look at chunks independently and still miss nothing.
Proving that to yourself is worth more than the code.

    python3 task4_son.py
    python3 task4_son.py --spark

Optional. Not part of the assignment.
"""
import argparse
import time
from collections import Counter
from itertools import combinations


def son_pass_one(chunks, support, total_baskets):
    """Find candidates frequent in at least one chunk.

    Each chunk gets a threshold scaled by its fraction of the full dataset.

    Return a set of frozensets.
    """
    candidates = set()

    for chunk in chunks:
        if not chunk:
            continue

        # SON scaled threshold:
        # local threshold = global support * chunk fraction
        scaled_support = support * len(chunk) / total_baskets

        # Local A-Priori pass 1: count singletons
        item_counts = Counter()

        for basket in chunk:
            item_counts.update(basket)

        local_frequent_items = {
            item
            for item, count in item_counts.items()
            if count >= scaled_support
        }

        # Local A-Priori pass 2:
        # only count pairs whose items survived local pass one
        pair_counts = Counter()

        for basket in chunk:
            items = sorted(
                item
                for item in basket
                if item in local_frequent_items
            )

            for pair in combinations(items, 2):
                pair_counts[pair] += 1

        # Any pair frequent in this chunk becomes a global candidate
        for pair, count in pair_counts.items():
            if count >= scaled_support:
                candidates.add(frozenset(pair))

    return candidates


def son_pass_two(baskets, candidates, support):
    """Count only SON candidates over all baskets.

    Pass one may produce false positives.
    Pass two removes them using the real global support.

    Return {frozenset: count}.
    """
    # Convert candidates to sorted tuples so basket combinations
    # can be checked directly and efficiently.
    candidate_pairs = {
        tuple(sorted(candidate))
        for candidate in candidates
    }

    counts = Counter()

    # Instead of:
    #   every candidate x every basket
    #
    # generate the pairs actually present in each basket
    # and check whether each one is a SON candidate.
    for basket in baskets:
        items = sorted(basket)

        for pair in combinations(items, 2):
            if pair in candidate_pairs:
                counts[pair] += 1

    return {
        frozenset(pair): count
        for pair, count in counts.items()
        if count >= support
    }


# ------------------------------------------------------------------- harness
def chunked(baskets, n_chunks):
    size = max(
        1,
        (len(baskets) + n_chunks - 1) // n_chunks
    )

    return [
        baskets[i:i + size]
        for i in range(0, len(baskets), size)
    ]


def spark_son(baskets, support, n_chunks):
    """SON as an actual two-pass MapReduce job. Given, for comparison."""
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("w06")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    total = len(baskets)

    rdd = (
        sc.parallelize(baskets, n_chunks)
        .map(lambda b: sorted(b))
        .cache()
    )

    def local_frequent(it):
        chunk = list(it)

        if not chunk:
            return []

        scaled = support * len(chunk) / total

        counts = {}

        for basket in chunk:
            for pair in combinations(basket, 2):
                counts[pair] = counts.get(pair, 0) + 1

        return [
            p
            for p, c in counts.items()
            if c >= scaled
        ]

    candidates = set(
        rdd.mapPartitions(local_frequent)
        .distinct()
        .collect()
    )

    bc = sc.broadcast(candidates)

    def count_candidates(it):
        counts = {}

        for basket in it:
            s = set(basket)

            for pair in bc.value:
                if s.issuperset(pair):
                    counts[pair] = counts.get(pair, 0) + 1

        return counts.items()

    final = (
        rdd.mapPartitions(count_candidates)
        .reduceByKey(lambda a, b: a + b)
        .filter(lambda kv: kv[1] >= support)
        .collectAsMap()
    )

    spark.stop()

    return (
        {frozenset(k): v for k, v in final.items()},
        len(candidates)
    )


def main():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--spark",
        action="store_true"
    )

    p.add_argument(
        "--chunks",
        type=int,
        default=8
    )

    a = p.parse_args()

    import bench
    from task3_pcy import PlainApriori

    baskets = bench.build()
    support = bench.SUPPORT

    print(
        f"\n  {len(baskets):,} baskets, support {support}, "
        f"{a.chunks} chunks\n"
    )

    # Task 3 baseline
    t0 = time.perf_counter()

    truth = PlainApriori(support).run(baskets)

    print(
        f"  task 3 baseline   "
        f"{time.perf_counter() - t0:7.2f}s   "
        f"pairs {len(truth):>6,}"
    )

    # Your SON
    try:
        t0 = time.perf_counter()

        cands = son_pass_one(
            chunked(baskets, a.chunks),
            support,
            len(baskets)
        )

        found = son_pass_two(
            baskets,
            cands,
            support
        )

        t_son = time.perf_counter() - t0

        missing = len(
            set(truth) - set(found)
        )

        extra = len(
            set(found) - set(truth)
        )

        print(
            f"  your SON          "
            f"{t_son:7.2f}s   "
            f"pairs {len(found):>6,}   "
            f"candidates {len(cands):>7,}   "
            f"missing {missing}, extra {extra}"
        )

        if missing:
            print(
                "    ^ SON must not have false negatives. "
                "Re-read §6.4.3 on the scaled threshold."
            )

    except NotImplementedError:
        print(
            "  your SON          "
            "TASK 4a / 4b not implemented"
        )

    # Optional Spark version
    if a.spark:
        try:
            t0 = time.perf_counter()

            sp, n_cand = spark_son(
                baskets,
                support,
                a.chunks
            )

            t_spark = time.perf_counter() - t0

            missing = len(
                set(truth) - set(sp)
            )

            print(
                f"  spark SON         "
                f"{t_spark:7.2f}s   "
                f"pairs {len(sp):>6,}   "
                f"candidates {n_cand:>7,}   "
                f"missing {missing}"
            )

        except Exception as e:
            print(
                f"  spark SON         "
                f"did not run: {type(e).__name__}"
            )

            print(
                "  Record it in observation.md - "
                "this task is optional for that reason."
            )

    print()


if __name__ == "__main__":
    main()