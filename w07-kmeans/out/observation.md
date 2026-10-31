# Week 7 Observations

## Task 1
Random initialization can converge to very different local optima even on the same nine points: the SSE ranged from `0.120` to `96.120`. With k-means++, the mean SSE was `0.120`, much lower than random initialization's `38.513`, because the initial centroids are spread out more deliberately.

For empty clusters, I kept the previous centroid instead of moving it arbitrarily. This keeps the algorithm stable and avoids introducing a new centroid position that was not justified by the current assignments.

## Task 2
As dimension increased, distance contrast collapsed: it fell below `1.0` at 50 dimensions and below `0.5` at 200 dimensions, reaching only `0.153` at 1000 dimensions. Relative standard deviation also fell from `0.476` in 2D to `0.019` in 1000D, showing that distances concentrate around the mean.

At 100 dimensions, increasing the number of sampled points from 200 to 5000 changed contrast from `0.536` to `0.721`, but relative standard deviation stayed near `0.06`. The Euclidean-distance concentration observed here does not directly prove the same effect for Week 3's Jaccard similarity because the representation and similarity measure are different.

## Task 3
The baseline used `10,320,000` distance computations, while my bounded version used only `1,150,986`, an `88.8%` reduction, with exactly the same SSE `10,737,882.94` and the same 43 iterations. The speed also improved from about `58.39s` to `9.24s`.

The pruning is exact because triangle inequality gives safe upper and lower bounds. If a point's upper bound to its current centroid is smaller than the lower bound to every competing centroid, no competing centroid can be closer, so the point can be skipped without calculating those distances; if the bound is not strong enough, the exact distances are measured.
