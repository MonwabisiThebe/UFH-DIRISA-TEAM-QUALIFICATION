# Model validation

## Design

Rolling-origin (time-series) validation, never random splits:

| Fold | Trains on targets | Role |
|---|---|---|
| 2011 | 2006 | validation |
| 2016 | 2006, 2011 | validation |
| 2021 | 2006, 2011, 2016 | final test, reported once |

Methods are chosen on the validation folds only. Tests in `tests/test_outputs.py` re-derive each selection from the
saved validation scores to prove the 2021 fold played no part.

## Data validation

| Check | Result |
|---|---|
| Registered voters vs IEC official reports, 2016 and 2021 (33 municipalities each) | exact match |
| Turnout vs IEC official reports | mean absolute difference 0.32 (2016) and 0.31 (2021) points; r > 0.99 |
| Province registered voters 2000, 2006, 2011 | 2011 exact; 2000 and 2006 gaps fully explained (Umzimkulu; DMA voters) |
| Rebuilt pipeline vs earlier prototype outputs | identical to floating-point precision |

## Turnout: relative position (points)

| Model | 2011 val | 2016 val | Mean val | 2021 test |
|---|---|---|---|---|
| **Relative persistence (selected)** | 4.23 | 1.57 | **2.90** | **2.08** |
| Shrunk persistence | 3.50 | 2.62 | 3.06 | 2.24 |
| Random forest | 3.73 | 2.48 | 3.11 | 2.34 |
| Ridge regression | 3.79 | 2.83 | 3.31 | 2.35 |
| Provincial average | 3.62 | 3.35 | 3.48 | 2.98 |

2021 test correlation between predicted and actual relative turnout: r = 0.77.

**Full turnout.** Adding a provincial level from earlier elections gives 2021 MAE of about 8.2 points for every
method, with predictions too high by 8.2 points on average: the error is the province-wide fall, which no municipal
model could anticipate. Hence the provincial level is a scenario assumption in 2026.

**Census check (supplementary).** Ridge trained on 2016, tested on 2021: electoral history only 1.90; plus Census 2011
2.10; Census 2011 only 3.16. Census information adds no forecasting value beyond past turnout. (That a ridge model
trained only on 2016 scores 1.90 is disclosed but not acted on: adopting it would be selection on the test year.)

## Party support (percentage points)

| Approach | Overall MAE | Largest party correct | ANC | DA | EFF | UDM | ATM | OTHER |
|---|---|---|---|---|---|---|---|---|
| **Selected by validation** | **2.69** | 33/33 | 3.89 | 2.67 | 3.19 | 0.98 | 2.00 | 3.38 |
| No change (baseline) | 2.93 | 33/33 | 4.50 | 2.81 | 3.17 | 1.00 | 2.00 | 4.10 |
| Last swing (trend continues) | 3.18 | 31/33 | 3.27 | 5.13 | 2.61 | 1.10 | 2.00 | 4.96 |
| Prototype (chosen on 2021: invalid) | 2.50 | 32/33 | – | – | – | – | – | – |

Selected methods: no change for ANC, DA, UDM (validated) and EFF, ATM (no validation fold, default rule); random forest
for OTHER. Identifying the largest party is an easy test here because leadership rarely changes; contest closeness is
the informative output (Nelson Mandela Bay 2021 gap: 0.44 points).

## Error scales carried into 2026

- Turnout: ±3.79 points (80th percentile of historical absolute municipal errors). Excludes provincial-level uncertainty.
- Party shares: 2.69 points (2021 test MAE); "too close to call" below a 5.37-point lead.
- Neither is a probabilistic confidence interval.
