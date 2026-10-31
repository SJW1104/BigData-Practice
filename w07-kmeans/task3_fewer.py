#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster without measuring it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)

        for self.iterations in range(1, self.max_iter + 1):
            changed = False

            for i, p in enumerate(points):
                best, bi = None, 0

                for j, c in enumerate(centroids):
                    d = distance(p, c)

                    if best is None or d < best - 1e-12:
                        best, bi = d, j

                if labels[i] != bi:
                    labels[i] = bi
                    changed = True

            centroids = _means(
                points,
                labels,
                self.k,
                centroids
            )

            if not changed:
                break

        return labels, centroids


def _means(points, labels, k, previous):
    out = []

    for j in range(k):
        group = [
            p
            for p, l in zip(points, labels)
            if l == j
        ]

        if group:
            out.append(
                tuple(
                    sum(v) / len(group)
                    for v in zip(*group)
                )
            )
        else:
            out.append(previous[j])

    return out


class YourKMeans:
    """Exact k-means using triangle-inequality bounds.

    For every point we keep:

        upper[i]
            upper bound on the distance to its current centroid

        lower[i]
            lower bound on the distance to the nearest competing centroid

    If the upper bound is already smaller than the lower bound, the point
    cannot possibly change cluster, so no point-centroid distance is needed.
    """

    def __init__(self, k, max_iter=50):
        self.k = k
        self.max_iter = max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        n = len(points)

        if n == 0:
            self.iterations = 0
            return [], centroids

        labels = [0] * n

        # upper[i]:
        # upper bound on distance to assigned centroid
        upper = [0.0] * n

        # lower[i]:
        # lower bound on distance to nearest competing centroid
        lower = [0.0] * n

        # ------------------------------------------------------------
        # First iteration
        #
        # No bounds exist yet, so every point must be compared with
        # every centroid.
        # ------------------------------------------------------------
        changed = False

        for i, p in enumerate(points):
            best = None
            second = None
            bi = 0

            for j, c in enumerate(centroids):
                d = distance(p, c)

                if best is None or d < best - 1e-12:
                    second = best
                    best = d
                    bi = j

                elif second is None or d < second:
                    second = d

            labels[i] = bi

            upper[i] = best

            lower[i] = (
                second
                if second is not None
                else float("inf")
            )

            changed = True

        # ------------------------------------------------------------
        # Remaining iterations
        # ------------------------------------------------------------
        for self.iterations in range(
            1,
            self.max_iter + 1
        ):

            old_centroids = centroids

            centroids = _means(
                points,
                labels,
                self.k,
                old_centroids
            )

            if not changed:
                break

            if self.iterations == self.max_iter:
                break

            # --------------------------------------------------------
            # Measure how far each centroid moved.
            #
            # Only k measurements instead of n * k.
            # --------------------------------------------------------
            movement = [
                distance(
                    old_centroids[j],
                    centroids[j]
                )
                for j in range(self.k)
            ]

            max_move = (
                max(movement)
                if movement
                else 0.0
            )

            # --------------------------------------------------------
            # Update point bounds using centroid movement.
            #
            # If my centroid moved by m:
            #     distance may increase by at most m.
            #
            # If another centroid moved by at most max_move:
            #     its distance may decrease by at most max_move.
            # --------------------------------------------------------
            for i in range(n):
                upper[i] += movement[labels[i]]

                lower[i] = max(
                    0.0,
                    lower[i] - max_move
                )

            # --------------------------------------------------------
            # Half the distance to the nearest other centroid.
            #
            # If a point is closer to its own centroid than this value,
            # triangle inequality proves no other centroid can win.
            # --------------------------------------------------------
            half_sep = [
                float("inf")
                for _ in range(self.k)
            ]

            for a in range(self.k):
                for b in range(a + 1, self.k):

                    d = distance(
                        centroids[a],
                        centroids[b]
                    ) * 0.5

                    if d < half_sep[a]:
                        half_sep[a] = d

                    if d < half_sep[b]:
                        half_sep[b] = d

            changed = False

            # --------------------------------------------------------
            # Reassign points only when bounds cannot prove that the
            # current assignment is still correct.
            # --------------------------------------------------------
            for i, p in enumerate(points):

                current = labels[i]

                bound = max(
                    lower[i],
                    half_sep[current]
                )

                # Cheap pruning test.
                #
                # Current centroid is definitely still the closest.
                if upper[i] < bound - 1e-12:
                    continue

                # ----------------------------------------------------
                # Tighten upper bound with one exact distance.
                # ----------------------------------------------------
                d_current = distance(
                    p,
                    centroids[current]
                )

                upper[i] = d_current

                if d_current < bound - 1e-12:
                    continue

                # ----------------------------------------------------
                # Bounds are not strong enough.
                # Do the exact comparison against all centroids.
                #
                # Reuse d_current so current centroid is not measured
                # twice.
                # ----------------------------------------------------
                best = None
                second = None
                bi = 0

                for j, c in enumerate(centroids):

                    if j == current:
                        d = d_current
                    else:
                        d = distance(p, c)

                    if best is None or d < best - 1e-12:
                        second = best
                        best = d
                        bi = j

                    elif second is None or d < second:
                        second = d

                if bi != current:
                    labels[i] = bi
                    changed = True

                upper[i] = best

                lower[i] = (
                    second
                    if second is not None
                    else float("inf")
                )

        return labels, centroids