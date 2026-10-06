# Week 3 Observations

## Task 1
I used one pass over the rows so the matrix does not need to be rescanned once for every column, which is important when the data is too large to fit comfortably in memory. If the signature length does not divide evenly by the number of bands, I place the leftover rows in the final band. S1–S4 was estimated as 1.0 although the true Jaccard value is 2/3; using more hash functions would reduce this sampling error, at the cost of more computation and memory.

## Task 2
On this Windows 11 machine (Intel64 Family 6 Model 181, 15.5 GB RAM), the measured crossover was between n = 3,500 and n = 4,000; at 4,000, brute force took 53.79 s while LSH took 48.45 s. Doubling n gave brute-force time multipliers of about 3.32×, 3.56×, 4.16×, and 5.78×, broadly matching quadratic growth with larger machine-level effects at the biggest size. n = 4,000 was the first unpleasant point because the wait approached one minute.

## Task 3
I used n = 120 hashes and b = 30 bands, so r = 4 rows per band and the S-curve step is approximately (1/30)^(1/4) = 0.427, intentionally below the 0.6 similarity threshold to favor recall. This gives P(candidate at s=0.6) = 1 - (1 - 0.6^4)^30 ≈ 98.45%; the final run reached 100% recall with only 123 exact comparisons. Moving the step in the wrong direction with 200 hashes, 40 bands, and 5 rows reduced recall to 70.2%; at much larger scale, treating hashing as free would stop being realistic because signature construction and bucket storage would themselves consume substantial CPU time and memory.
