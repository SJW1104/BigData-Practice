# Week 6 Observations

## Task 1

Confidence depends on direction because the denominator is the support of the antecedent. For example, `cola -> milk` has confidence `2/2 = 1.0`, while `milk -> cola` is `2/5 = 0.4`; `cola -> milk` is the more useful directional claim, although cola itself does not pass support 3.

Among the frequent rules, `diaper -> beer` has confidence `0.8` and lift about `1.12`, so I would not consider it a very strong relationship because beer is already common. With 2,000 items, brute force has `2,000 × 1,999 / 2 = 1,999,000` possible pairs, while A-Priori avoids creating counters involving items that fail pass one.

## Task 2

Lowering support from 400 to 200 increased peak counters from `10,585` to `58,626` (about `5.5×`), and lowering it again to 100 increased them to `273,701` (about `4.7×`). The counter count eventually saturated at `893,456`.

The answers grew differently: at support 25 there were only `17,045` frequent pairs even though `893,456` counters were needed. My machine remained usable down to support 1, where all `893,456` candidates were frequent and peak traced memory reached `334.2 MB`.

## Task 3

PCY found exactly the same `6,397` frequent pairs as Plain A-Priori with `missing 0` and `extra 0`, while reducing peak pair counters from `820,259` to `23,356`, a `97.2%` reduction. I used `1,000,003` buckets so the bitmap would be selective enough to eliminate most pass-two candidates.

The bucket array is itself a fixed memory cost, so PCY becomes more useful when the pair-counter dictionary grows larger than that overhead. When I reduced the bucket count to `100,003`, peak pair counters increased to `197,627` because more unrelated pairs collided into frequent buckets; the smaller bucket array saved fixed memory but weakened the filtering power.

## Task 4

With `4`, `8`, and `16` chunks, SON generated `9,876`, `14,201`, and `24,418` candidates respectively, while the final result stayed exactly `6,397` pairs with `missing 0` and `extra 0`. The candidate count changes with chunking, but the final answer does not because pass two checks the candidates against the global support.

A globally frequent pair cannot be missed by every chunk: if its count were below the scaled threshold in every chunk, adding those counts would make its global count lower than the global support, which is a contradiction. SON is useful even though it adds chunking overhead because the chunks can be processed independently when the complete dataset does not fit on one machine. Spark could not run because `pyspark` was not installed (`ModuleNotFoundError`).