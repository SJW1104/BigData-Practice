#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a local optimum, and which one depends entirely on where you
started.

    python3 task1_kmeans.py --verify
"""
import argparse
import math
import random


BLOBS = [
    (0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
    (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
    (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)
]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    return math.sqrt(
        sum((x - y) ** 2 for x, y in zip(a, b))
    )


def assign(points, centroids):
    """Nearest centroid for each point.

    Ties go to the lower centroid index.
    """
    labels = []

    for p in points:
        best_index = 0
        best_distance = euclidean(p, centroids[0])

        for i in range(1, len(centroids)):
            d = euclidean(p, centroids[i])

            if d < best_distance - 1e-12:
                best_distance = d
                best_index = i

        labels.append(best_index)

    return labels


def update(points, labels, k, previous=None):
    """Move each centroid to the mean of its assigned points.

    Empty-cluster policy:
    keep the previous centroid if it is available.
    """
    centroids = []

    for cluster in range(k):
        group = [
            p
            for p, label in zip(points, labels)
            if label == cluster
        ]

        if group:
            centroid = tuple(
                sum(values) / len(group)
                for values in zip(*group)
            )
            centroids.append(centroid)

        elif previous is not None:
            centroids.append(previous[cluster])

        else:
            # This branch is only a fallback if update() is called directly
            # without previous centroids.
            centroids.append(tuple(0.0 for _ in points[0]))

    return centroids


def _random_initialisation(points, k, rng):
    """Pick k different input points at random."""
    return list(rng.sample(points, k))


def _plusplus_initialisation(points, k, rng):
    """k-means++ initialisation."""
    centroids = [rng.choice(points)]

    while len(centroids) < k:
        squared_distances = []

        for p in points:
            nearest = min(
                euclidean(p, c)
                for c in centroids
            )
            squared_distances.append(nearest ** 2)

        total = sum(squared_distances)

        # All points already coincide with selected centroids.
        if total <= 0:
            remaining = [
                p for p in points
                if p not in centroids
            ]

            if not remaining:
                break

            centroids.append(rng.choice(remaining))
            continue

        target = rng.random() * total
        cumulative = 0.0
        chosen = points[-1]

        for p, weight in zip(points, squared_distances):
            cumulative += weight

            if cumulative >= target:
                chosen = p
                break

        centroids.append(chosen)

    return centroids


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run k-means to convergence.

    Return:
        labels, centroids, sse
    """
    if not points:
        raise ValueError("points must not be empty")

    if k <= 0 or k > len(points):
        raise ValueError("k must be between 1 and number of points")

    rng = random.Random(seed)

    if init == "random":
        centroids = _random_initialisation(points, k, rng)

    elif init == "++":
        centroids = _plusplus_initialisation(points, k, rng)

    else:
        raise ValueError("init must be 'random' or '++'")

    labels = [None] * len(points)

    for iteration in range(1, max_iter + 1):
        new_labels = assign(points, centroids)

        new_centroids = update(
            points,
            new_labels,
            k,
            previous=centroids
        )

        labels_changed = new_labels != labels

        centroid_changed = any(
            euclidean(old, new) > 1e-12
            for old, new in zip(centroids, new_centroids)
        )

        labels = new_labels
        centroids = new_centroids

        if not labels_changed or not centroid_changed:
            kmeans.iterations = iteration
            break

    else:
        kmeans.iterations = max_iter

    return labels, centroids, sse_of(points, labels, centroids)


def sse_of(points, labels, centroids):
    """Sum of squared distances to each point's assigned centroid."""
    total = 0.0

    for p, label in zip(points, labels):
        d = euclidean(p, centroids[label])
        total += d ** 2

    return total


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check(
            "distance in 2d",
            abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9
        )

        check(
            "distance in 5d",
            abs(
                euclidean(
                    (0,) * 5,
                    (1,) * 5
                ) - math.sqrt(5)
            ) < 1e-9
        )

    except NotImplementedError:
        print("  euclidean is still a stub")
        return 1

    try:
        labels, cents, sse = kmeans(
            BLOBS,
            3,
            init="++",
            seed=1
        )

    except NotImplementedError:
        print("  kmeans is still a stub")
        return 1

    groups = {}

    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)

    check(
        "three clusters of three",
        sorted(len(g) for g in groups.values()) == [3, 3, 3],
        sorted(len(g) for g in groups.values())
    )

    check(
        "the three blobs were recovered",
        all(
            max(q[0] for q in g) - min(q[0] for q in g) < 1
            and
            max(q[1] for q in g) - min(q[1] for q in g) < 1
            for g in groups.values()
        )
    )

    check(
        "sse is small when clusters are right",
        sse < 1.0,
        f"sse {sse:.4f}"
    )

    randoms = [
        kmeans(
            BLOBS,
            3,
            init="random",
            seed=s
        )[2]
        for s in range(40)
    ]

    plusplus = [
        kmeans(
            BLOBS,
            3,
            init="++",
            seed=s
        )[2]
        for s in range(40)
    ]

    check(
        "random init sometimes lands badly",
        max(randoms) > min(randoms) * 5,
        f"sse from {min(randoms):.3f} to {max(randoms):.3f}"
    )

    check(
        "k-means++ is more reliable than random",
        sum(plusplus) / len(plusplus)
        <=
        sum(randoms) / len(randoms),
        f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
        f"random {sum(randoms) / len(randoms):.3f}"
    )

    print(
        f"\n  {'all ok' if not fails else str(fails) + ' failed'}"
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