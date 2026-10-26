# Task 2 - Threshold Explosion

## Measurements

| Support | Frequent pairs | Peak counters | Seconds | Peak memory |
|---:|---:|---:|---:|---:|
| 400 | 249 | 10,585 | 0.61 | 1.1 MB |
| 200 | 776 | 58,626 | 1.08 | 6.7 MB |
| 100 | 2,244 | 273,701 | 2.29 | 28.6 MB |
| 50 | 6,397 | 820,259 | 3.33 | 107.7 MB |
| 25 | 17,045 | 893,456 | 3.77 | 107.7 MB |
| 12 | 43,116 | 893,456 | 4.63 | 110.0 MB |
| 6 | 101,938 | 893,456 | 4.30 | 126.5 MB |
| 3 | 250,054 | 893,456 | 4.63 | 163.9 MB |
| 2 | 424,620 | 893,456 | 8.28 | 212.0 MB |
| 1 | 893,456 | 893,456 | 5.69 | 334.2 MB |

## A2 - Where It Became Unpleasant

The program remained runnable down to support 1, so this dataset did not cause an actual failure on my machine. At support 1, all 893,456 candidate pairs became frequent and peak traced memory reached 334.2 MB. Since support 1 is the minimum possible threshold, there was no lower value left to test.

## A4 - Counter Growth

The number of peak counters grew much faster than linearly at the higher support thresholds. Lowering support from 400 to 200 increased peak counters from 10,585 to 58,626, about 5.5 times. Lowering it again from 200 to 100 increased the count to 273,701, about 4.7 times.

At support 25, the counter count reached 893,456 and then stopped increasing. This shows that counter growth was much worse than simply doubling during the earlier threshold reductions.

## A5 - Frequent Pairs vs. Counters

The number of actual frequent pairs grew differently from the number of counters. At support 25, 893,456 pair counters were already required even though only 17,045 pairs were actually frequent.

As support decreased further, the number of counters stayed fixed at 893,456 while the number of frequent pairs continued to grow, eventually reaching 893,456 at support 1.

This gap is the main problem with lowering support: the algorithm may need to maintain a very large number of candidate counters even when only a much smaller fraction become final answers.

## A6 - Machine

- CPU: 12th Gen Intel Core i5-1240P
- RAM: 15.6 GB
- Python: 3.14.7
- Other programs running: VS Code, Chrome, ChatGPT, KakaoTalk, and File Explorer