# Model Validation

## Turnout
The project uses temporal backtesting rather than random-row splitting. On the 2021 holdout, the Average Change Baseline recorded the lowest MAE at approximately 7.725 percentage points. Persistence was approximately 8.204, Random Forest 8.795, Ridge 9.428 and Linear Regression 9.527. The result demonstrates that additional model complexity did not improve generalisation on this holdout.

The earlier 2016 temporal validation was easier: persistence MAE was approximately 2.492 percentage points. The deterioration in 2021 is retained as evidence of temporal instability and forecast uncertainty.

## Party support
Category-specific model selection produced an overall reconstructed 2021 party-share MAE of approximately 2.502 percentage points. The category with the largest reconstructed share matched the observed largest-share category in 32 of 33 municipalities. This is a historical diagnostic and is not treated as a guarantee for 2026.
