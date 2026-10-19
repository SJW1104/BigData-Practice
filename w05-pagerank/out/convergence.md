# Task 2 · PageRank Convergence

## A2. Iterations by beta

| beta | nodes | tol | iterations | seconds |
|---:|---:|---:|---:|---:|
| 0.50 | 1200 | 1e-10 | 14 | 0.025 |
| 0.70 | 1200 | 1e-10 | 17 | 0.038 |
| 0.85 | 1200 | 1e-10 | 20 | 0.055 |
| 0.95 | 1200 | 1e-10 | 23 | 0.074 |
| 0.99 | 1200 | 1e-10 | 24 | 0.067 |

## A3. Effect of beta

As beta approaches 1, the number of iterations increases. In my measurements it increased from 14 iterations at beta=0.50 to 24 iterations at beta=0.99.

A larger beta means the random surfer follows links more often and teleports less often, so the rank distribution depends more strongly on repeated propagation through the graph and takes longer to converge.

## A4. Graph size

At beta=0.85, increasing the graph from 1,200 nodes to 20,000 nodes changed the iteration count only from 20 to 21, while wall time increased from about 0.055 s to 0.922 s.

At beta=0.95, the iteration count changed from 23 to 24, while wall time increased from about 0.074 s to 0.921 s. Therefore graph size had little effect on iteration count, but greatly increased wall time because every iteration had more nodes and edges to process.

## A5. Tolerance

For beta=0.85:

| tolerance | iterations | seconds |
|---:|---:|---:|
| 1e-4 | 9 | 0.015 |
| 1e-6 | 12 | 0.024 |
| 1e-10 | 20 | 0.055 |

Tightening the tolerance from 1e-4 to 1e-6 required 3 additional iterations, and tightening it from 1e-6 to 1e-10 required 8 more iterations.

This is roughly 1.5 to 2 additional iterations for each extra decimal digit of precision.

## A6. Top-10 ranking

The top three pages stayed the same for every tested beta: p00009, p00001, and p00006.

However, the full top-10 order first changed at beta=0.70. At beta=0.50, p00000 ranked above p00004, while from beta=0.70 onward p00004 ranked above p00000.

This shows that beta can affect the ranking itself, not only convergence speed, so the chosen beta matters when interpreting a published PageRank result.

## A7. Machine

- CPU: 12th Gen Intel Core i5-1240P
- RAM: 15.6 GB
- OS: Windows 11
- Python: 3.14.7
- Other programs running: VS Code, KakaoTalk, File Explorer, Chrome, ChatGPT