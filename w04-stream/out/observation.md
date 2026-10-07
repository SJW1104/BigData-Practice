# Observations

## Task 1
Bloom filters cannot have false negatives because `add` sets every bit later checked by `__contains__`; the predicted FP rate was 0.860% and the measured rate was 0.775%.
For FM I used the median of the register estimates: it gave 21,181 for a truth of 19,953, while a direct mean was dominated by an outlier and produced a much less stable estimate.
Reservoir sampling stays at `k` items; `j = rng.randrange(i + 1)` followed by replacement only when `j < k` gives every seen item final probability `k/n` without knowing `n` ahead of time.

## Task 2
Exact counting became impractical at 12,800,000 items: it took 22.10 s and 377.6 MB; RAM did not run out, but waiting time became the first practical limit.
From 400,000 to 12,800,000 items, exact memory grew about 32.55x for 32x more input, showing roughly `O(n)` memory growth, while FM stayed near 0.004–0.005 MB, or `O(1)` space.
A factor-of-two estimate is acceptable for rough capacity planning, but not for billing or compliance where the exact distinct-user count affects money or obligations.

## Task 3
I chose `k = round((m/n) ln 2) = round(10 ln 2) = 7` hashes, the minimizer of `(1 - e^(-kn/m))^k` for 10 bits per item.
The theoretical floor is `(0.6185)^10 ≈ 0.819%`; the measured rate was 0.820% with zero false negatives, very close to the floor and 91.4% below the 9.511% baseline.
If `n` were unknown, I would use a scalable Bloom filter and add a new filter as capacity is reached; guessing low saturates the bits and raises false positives, while guessing high wastes memory.