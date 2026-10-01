# EVALUATION EXPLAINER

EnergyInvest is evaluated as a **triage system**, not merely as a binary classifier.

## Holdout design
A grouped holdout uses `GEM location ID`, keeping units or phases from the same facility in the same split.

- Resolved records: 142,575
- Training records: 113,991
- Holdout records: 28,584

## Metrics

### High-risk recall
**Reached: 91.58%**

Measures how many historical high-risk cases are brought to analyst attention.

### Flag rate
**Reached: 25.17%**

`(High Risk + Needs Manual Review) / all holdout projects`

This directly measures how much analyst work remains.

### Workload reduction
**Reached: 74.83%**

`1 - flag rate`

### Precision among flagged projects
**Reached: 35.83%**

This exposes the false-positive burden and shows why the model is suitable for screening, not automatic investment recommendation.

### Abstention rate
**Reached: 11.03%**

This quantifies how often the system refuses to force a binary decision. Abstained cases count as analyst workload.

## Subgroup recall

| Historical outcome | Recall |
|---|---:|
| confirmed `cancelled` | 91.46% |
| `cancelled - inferred 4 y` | 91.25% |
| `shelved` | 91.21% |
| `shelved - inferred 2 y` | 92.45% |

## Baselines

**Always Low:** recall 0%, flag rate 0%, workload reduction 100%.  
This saves all review work but misses every risky project.

**Always High:** recall 100%, flag rate 100%, workload reduction 0%.  
This demonstrates why recall alone is insufficient.

## Main critique
The model still misses **8.42% of historical high-risk holdout cases**. Precision is only **35.83%**, so many flagged cases are false positives. This is acceptable only for a triage workflow where additional review is cheaper than overlooking a genuinely risky project.

## Files
- `metrics.json`: aggregate results
- `holdout_predictions.csv`: row-level holdout outputs for audit and error analysis
