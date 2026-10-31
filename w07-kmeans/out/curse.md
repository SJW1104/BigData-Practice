# Task 2 - Curse of Dimensionality

## Measurements

| Dimension | Points | Mean | Min | Max | Contrast | Relative SD |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1000 | 0.521 | 0.003 | 1.326 | 488.582 | 0.476 |
| 5 | 1000 | 0.884 | 0.111 | 1.687 | 14.257 | 0.282 |
| 10 | 1000 | 1.274 | 0.438 | 2.159 | 3.925 | 0.193 |
| 20 | 1000 | 1.815 | 0.821 | 2.670 | 2.253 | 0.135 |
| 50 | 1000 | 2.867 | 1.909 | 3.785 | 0.982 | 0.083 |
| 100 | 1000 | 4.068 | 3.206 | 4.954 | 0.545 | 0.060 |
| 200 | 1000 | 5.776 | 4.871 | 6.682 | 0.372 | 0.041 |
| 500 | 2000 | 9.126 | 8.099 | 10.176 | 0.256 | 0.026 |
| 1000 | 2000 | 12.909 | 11.970 | 13.806 | 0.153 | 0.019 |
| 100 | 200 | 4.084 | 3.228 | 4.957 | 0.536 | 0.059 |
| 100 | 5000 | 4.076 | 3.045 | 5.242 | 0.721 | 0.060 |

## A3 - Contrast as Dimension Increases

The contrast decreased rapidly as dimension increased. It first fell below `1.0` at dimension 50, where the contrast was `0.982`, and it first fell below `0.5` at dimension 200, where it was `0.372`.

At dimension 1000, the contrast was only `0.153`. This shows that the nearest and farthest distances become much less distinguishable as dimension increases.

## A4 - Mean Distance

The mean distance increased with dimension, but not linearly. For example, the mean distance was `1.274` at dimension 10, `4.068` at dimension 100, and `12.909` at dimension 1000.

When dimension increased by a factor of 10, the mean distance increased by roughly a factor of 3.2, which is close to `sqrt(10)`. Therefore the measurements are consistent with mean Euclidean distance growing approximately with `sqrt(d)`.

## A5 - Relative Standard Deviation

Relative standard deviation also decreased strongly with dimension. It fell from `0.476` at dimension 2 to `0.060` at dimension 100 and to only `0.019` at dimension 1000.

Both contrast and relative standard deviation show distance concentration. Contrast directly compares the nearest and farthest observed distances, while relative standard deviation shows that the overall distribution of distances is becoming tightly concentrated around the mean.

## A6 - Changing the Number of Points

At dimension 100, using 200 points gave contrast `0.536`, 1000 points gave `0.545`, and 5000 points gave `0.721`. Therefore increasing the number of sampled points did not simply reduce contrast.

With more points, the sample is more likely to contain both an unusually close pair and an unusually distant pair, so the observed minimum and maximum can spread farther apart. However, relative standard deviation stayed almost unchanged at about `0.059-0.060`, showing that the overall distance distribution was still highly concentrated.

## A7 - Machine and Largest Run

- CPU: 12th Gen Intel Core i5-1240P
- RAM: 15.6 GB
- Python: 3.14.7

The largest experiment used 5000 points at dimension 100. The script completed successfully on this machine.

## A8 - Does This Also Threaten Week 3 LSH?

Not directly. This experiment measures Euclidean distance between points in a high-dimensional numeric unit cube, while Week 3 LSH used Jaccard similarity between sets.

The same general warning applies that high-dimensional representations can make similarity measures less discriminative, but the Euclidean distance concentration measured here does not by itself prove that Jaccard similarity will behave the same way. The effect depends on the data representation and the similarity or distance measure being used.
