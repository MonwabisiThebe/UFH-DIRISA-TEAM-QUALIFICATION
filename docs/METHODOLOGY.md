# Methodology

## Unit and scope
Eastern Cape municipalities; Local Government Elections 2000, 2006, 2011, 2016 and 2021. Party-support analysis uses PR ballots.

## Historical harmonisation
Historical municipality codes are mapped into the project's 33-code analytical geography using an explicit crosswalk. The 2000 panel has 32 target municipalities; later elections have 33. Boundary harmonisation is an analytical approximation and is documented as a limitation.

## Competition measures
Victory margin is the percentage-point difference between the two largest PR party shares. Effective Number of Parties is `1 / sum(p_i^2)`, using the complete party distribution before grouping.

## Demographics
Municipality Census 2011 and 2022 values are retained as anchors. 2016 and 2021 values are linearly interpolated for descriptive historical alignment. Pre-2011 values are unavailable rather than back-extrapolated. Interpolated values that depend on the 2022 endpoint are not used as strict pre-2021 turnout predictors.

## Turnout validation
The primary prediction target is municipality turnout. Historical information available before the target election is used. Models are compared with simple baselines under temporal validation. MAE is the primary selection metric, with RMSE and R² as secondary metrics.

## Party-support validation
Selected PR categories are ANC, DA, EFF, UDM, ATM and OTHER. The target is change in party vote share. Methods are evaluated on the 2016→2021 holdout transition and selected separately by category using MAE. Predicted shares are constrained to non-negative values and renormalised to 100%.

## 2026 scenario construction
The lowest-error Phase 4 turnout method is carried forward. Party categories use their Phase 5 selected methods. Historical MAE is shown as sensitivity around central scenario values. These are not probabilistic confidence intervals.
