Data statistics:

| Table 1       | Corpus A      | Corpus B      |
|---------------|---------------|---------------|-----------|
| Posts         | 19131         | 19812         |           |
| Filesize      | 15750 kb      | 18887 kb      | in kb     |
| Avg Length    | 138.05 words  | 155.86 words  | per Post  |
| Median Length | 99.00 words   | 110.00 words  |     id.   |

Downsampled B-Corpus (19131 Posts):

| Table 2       | Corpus A      | Corpus B      |                |
|---------------|---------------|---------------|----------------|
| MTLD          | 96.70         | 107.37        | 0 (p-Value)    |
| Entropy       | 10.9068       | 11.1813       | 0.2745 (Diff)  |
| Entropy (POS) | 3.5722        | 3.5553        | -0.0170        |
| FWR           | 0.8643        | 0.8395        | -0.0248        |
| Avg PTD       | 5.32          | 5.28          | -0.03          |

-> Increased text density in Corpus B, while Parse-Tree-Depth remains structurally stable (not significant).

Reduction of Sample B -> A (B filtered on A) by Vocabulary Intersection:

| Table 3       | Corpus A      | Corpus B      | Difference     |
|---------------|---------------|---------------|----------------|
| Token-Count (A)| 264116       | id. to A      |                |
| Unique-Types  | 119655        | id. to A      |                |
| MTLD          | 117.88        | 116.62        | -1.26          |
| Entropy       | 10.9068       | 10.6515       | -0.2554        |
| Entropy (POS) | 3.5722        | 3.5553        | -0.0170        |

-> TOPIC-SHIFT impact leads to increased complexity. Without technical terminology texts becomes simpler.

Mann-Whitney-U:
U-Statistic: 184663006.00
p-Value: 0.1230617602
-> Result is not significant. Could be chance.
Absolute Difference: 0.0322