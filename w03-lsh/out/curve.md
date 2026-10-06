# Task 2 · Crossover Curve

## Machine

- Platform: Windows 11 (10.0.26200)
- CPU: Intel64 Family 6 Model 181 Stepping 0, GenuineIntel
- RAM: 15.5 GB
- Python: 3.14.7
- Other programs: VS Code / PowerShell were in use during the measurement.

## Measurements

| n | Brute time (s) | LSH time (s) | Brute comparisons | LSH comparisons | Brute peak memory (MiB) | LSH peak memory (MiB) |
|---:|---:|---:|---:|---:|---:|---:|
| 250 | 0.19 | 3.32 | 31,125 | 15 | 0.008 | 1.33 |
| 500 | 0.63 | 6.22 | 124,750 | 29 | 0.009 | 2.64 |
| 1,000 | 2.24 | 12.06 | 499,500 | 61 | 0.009 | 5.29 |
| 2,000 | 9.31 | 24.02 | 1,999,000 | 120 | 0.018 | 10.59 |
| 3,000 | 27.58 | 61.53 | 4,498,500 | 185 | 0.032 | 16.04 |
| 3,500 | 36.17 | 42.13 | 6,123,250 | 207 | 0.036 | 18.68 |
| 4,000 | 53.79 | 48.45 | 7,998,000 | 238 | 0.039 | 21.33 |

## A3 · Time against n

Brute force is faster at small n. LSH pays an up-front cost for generating MinHash signatures, splitting them into bands, and building buckets before it performs any exact similarity comparisons. As n grows, the quadratic all-pairs cost of brute force eventually overtakes that setup cost.

## A4 · Quadratic check

When n doubles, ideal quadratic growth predicts about 4× the runtime.

- 250 → 500: 0.63 / 0.19 ≈ 3.32×
- 500 → 1,000: 2.24 / 0.63 ≈ 3.56×
- 1,000 → 2,000: 9.31 / 2.24 ≈ 4.16×
- 2,000 → 4,000: 53.79 / 9.31 ≈ 5.78×

The first three doublings are close to the expected 4× trend, especially as n grows. The final point is slower than the ideal quadratic factor, which is consistent with additional real-machine effects such as cache, memory, and background system load.

## A5 · Peak memory at the largest n

At n = 4,000:

- Brute force peak traced memory: about 0.039 MiB
- LSH peak traced memory: about 21.33 MiB

LSH uses much more memory because it stores signatures, band keys, and buckets, while brute force mostly scans pairs directly.

## A7 · Crossover

At n = 3,500, brute force is still faster:

- Brute force: 36.17 s
- LSH: 42.13 s

At n = 4,000, LSH becomes faster:

- Brute force: 53.79 s
- LSH: 48.45 s

Therefore, the measured crossover on this machine is between n = 3,500 and n = 4,000.

## A8 · Why LSH loses at small n

LSH performs substantial work before any exact comparison: each document is hashed many times to build a MinHash signature, signatures are divided into bands, and band buckets are constructed. That work grows roughly linearly with n but has a large constant cost. For small datasets, brute force is simpler and finishes before the LSH setup cost is recovered.

## Unpleasant size

n = 4,000 was the first clearly unpleasant point in this run. Brute force took 53.79 seconds, which is close to one minute, while LSH took 48.45 seconds.
