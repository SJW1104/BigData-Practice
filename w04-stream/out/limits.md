# Task 2 — Exact Distinct Counting Limits

## Machine

- CPU: Intel(R) Core(TM) Ultra 5 225U
- RAM: 15.5 GB
- Python: 3.14.7
- Platform: Windows 11 (`Windows-11-10.0.26200-SP0`)
- Other software: PowerShell, ChatGPT/Codex, ordinary Windows background services, and OneDrive were active. The machine was not restarted into a dedicated benchmark environment.

## Measurements

| Stream size (`n`) | True distinct | Exact time | Exact peak memory | FM time | FM peak memory | FM / truth |
|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.21 s | 3.9 MB | 0.97 s | 0.004 MB | 1.15x |
| 400,000 | 146,970 | 0.94 s | 11.6 MB | 8.48 s | 0.004 MB | 2.31x |
| 1,600,000 | 587,625 | 5.30 s | 46.6 MB | 13.65 s | 0.004 MB | 1.15x |
| 6,400,000 | 2,349,909 | 15.61 s | 188.3 MB | 36.58 s | 0.005 MB | 1.15x |
| 12,800,000 | 4,699,458 | 22.10 s | 377.6 MB | 100.20 s | 0.005 MB | 1.15x |

The measurements cover five stream sizes and a 128x range, from 100,000 to 12,800,000 items.

## Where exact stopped being practical

The exact set began to feel inconvenient at `n = 6,400,000`, where it needed 15.61 seconds and 188.3 MB. At `n = 12,800,000`, it needed 22.10 seconds and 377.6 MB, making repeated interactive runs impractical. The run did not exhaust physical RAM or raise `MemoryError`; waiting time was the first practical limit, while the linear memory curve showed what would eventually run out.

## Memory growth

| Change in stream size | Change in exact memory |
|---|---:|
| 400,000 → 1,600,000 (4x) | 11.6 MB → 46.6 MB (4.02x) |
| 1,600,000 → 6,400,000 (4x) | 46.6 MB → 188.3 MB (4.04x) |
| 6,400,000 → 12,800,000 (2x) | 188.3 MB → 377.6 MB (2.01x) |

From 400,000 to 12,800,000 items, `n` grew 32x while exact peak memory grew about 32.55x, confirming approximately linear `O(n)` space. FM stayed near 0.004–0.005 MB because its memory is determined by 64 fixed registers, so its measured space was effectively `O(1)` in `n`.

FM was not faster in this Python implementation: at 12,800,000 items, exact counting took 22.10 seconds and FM took 100.20 seconds. Its advantage here was bounded memory rather than execution speed.

## FM accuracy

The FM-to-truth ratios were `1.15x`, `2.31x`, `1.15x`, `1.15x`, and `1.15x`. Accuracy did not improve or worsen monotonically with `n`; the 400,000-item run shows how a rare long trailing-zero hash can produce a coarse outlier. That value is retained because it is part of the observed error behavior.

A factor-of-two estimate is useful for rough capacity planning or determining an order of magnitude. It is not adequate for billing, financial settlement, or regulatory reporting where the distinct count directly determines money or obligations.
