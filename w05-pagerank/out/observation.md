# Week 5 Observations

## Task 1
Without the fix, rank at a dead end disappears because there is no outgoing link; I redistributed that dangling rank uniformly across all nodes instead.
Teleportation fixes both dead ends and spider traps by continually returning probability mass to the whole graph: with probability `beta` the surfer follows a link, and with probability `1 - beta` jumps to a uniformly chosen page.

## Task 2
As `beta` approached 1, convergence required more iterations (`14` at `0.50` versus `24` at `0.99`), while increasing the graph from 1,200 to 20,000 nodes barely changed the iteration count but greatly increased wall time.
The top-10 order first changed at `beta = 0.70` (`p00004` moved above `p00000`), although the top three pages remained `p00009`, `p00001`, and `p00006` for every tested beta.

## Task 3
Instead of storing the dense `n × n` transition matrix, I kept the graph as an adjacency list and stored only the rank vectors, reducing storage from `O(n²)` to roughly `O(n + E)`.
The teleport and dead-end terms do not need a dense matrix because every node receives the same scalar contribution each iteration, and the worst per-node difference from the dense answer was only `1.18e-15`, caused by floating-point accumulation order.