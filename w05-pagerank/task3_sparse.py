#!/usr/bin/env python3
"""Week 5 · Task 3 — PageRank on a graph that will not fit as a matrix.

Textbook §5.2 (efficient PageRank), §5.2.1 - §5.2.3.

`DenseMatrix` is PageRank written the way the equations are written: build the
transition matrix M, multiply. It is correct, it is easy to read, and it stores
n^2 numbers for a graph with almost no edges.

The web's matrix is about 99.9999% zeros. Storing them is the problem, and
§5.2 is the chapter about not doing that.

    python3 bench.py
    python3 bench.py --yours

Correctness first: the harness compares your ranks against the dense version
element by element. A fast PageRank that ranks pages differently is a different
algorithm, not a faster one.
"""


class DenseMatrix:
    """PageRank as written in the equations. Stores n^2 floats."""

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        index = {v: i for i, v in enumerate(nodes)}

        # the full transition matrix, zeros and all
        M = [[0.0] * n for _ in range(n)]
        for v, outs in graph.items():
            if outs:
                share = 1.0 / len(outs)
                for w in outs:
                    M[index[w]][index[v]] = share
            else:
                for i in range(n):           # dead end: spread it everywhere
                    M[i][index[v]] = 1.0 / n

        r = [1.0 / n] * n
        for self.iterations in range(1, self.max_iter + 1):
            nr = [0.0] * n
            for i in range(n):
                row = M[i]
                s = 0.0
                for j in range(n):
                    if row[j]:
                        s += row[j] * r[j]
                nr[i] = self.beta * s + (1 - self.beta) / n
            delta = sum(abs(a - b) for a, b in zip(nr, r))
            r = nr
            if delta < self.tol:
                break
        return {v: r[index[v]] for v in nodes}

    def memory_floats(self):
        return getattr(self, "_n", 0) ** 2


class YourPageRank:
    """Sparse PageRank using the graph's adjacency-list representation.

        __init__(beta=0.85, tol=1e-10, max_iter=100)
        run(graph) -> {node: rank}
        memory_floats() -> the largest number of floats held at once

    Instead of materialising an n x n transition matrix, this implementation
    keeps only the current and next rank vectors and follows the edges that
    actually exist.
    """

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta = beta
        self.tol = tol
        self.max_iter = max_iter
        self.iterations = 0
        self._memory_floats = 0

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)

        if n == 0:
            self.iterations = 0
            self._memory_floats = 0
            return {}

        index = {v: i for i, v in enumerate(nodes)}

        # Convert node names to integer indices once.
        # This is still sparse: only real edges are stored.
        adjacency = []
        dangling = []

        for v in nodes:
            outs = graph[v]

            if outs:
                adjacency.append([index[w] for w in outs])
            else:
                adjacency.append([])
                dangling.append(index[v])

        # Current PageRank vector.
        r = [1.0 / n] * n

        # At most two n-element float vectors are held at once.
        self._memory_floats = 2 * n

        teleport = (1.0 - self.beta) / n

        for step in range(1, self.max_iter + 1):
            # Sum rank held by dead-end nodes.
            dangling_rank = 0.0
            for i in dangling:
                dangling_rank += r[i]

            # Every node gets the same teleport contribution and the same
            # redistributed dead-end contribution. No dense matrix is needed.
            base = teleport + self.beta * dangling_rank / n
            nr = [base] * n

            # Follow only edges that actually exist.
            for src in range(n):
                outs = adjacency[src]

                if not outs:
                    continue

                share = self.beta * r[src] / len(outs)

                for dst in outs:
                    nr[dst] += share

            # L1 convergence test.
            delta = 0.0
            for i in range(n):
                delta += abs(nr[i] - r[i])

            r = nr
            self.iterations = step

            if delta < self.tol:
                break

        return {
            node: r[index[node]]
            for node in nodes
        }

    def memory_floats(self):
        return self._memory_floats