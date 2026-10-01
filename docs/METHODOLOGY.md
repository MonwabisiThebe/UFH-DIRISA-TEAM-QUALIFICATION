# Methodology

## Scope and unit

Eastern Cape; Local Government Elections 2000, 2006, 2011, 2016 and 2021; unit = municipality × election, on the 33
present-day municipalities. Party support uses the PR ballot throughout.

## 1. Historical elections (Notebook 01, `src/data/elections.py`)

1. Read both IEC schema generations (2000/2006 and 2011–2021) with the correct encodings.
2. Keep Eastern Cape PR-ballot rows.
3. Map historical municipality codes to the 33 analytical codes with the explicit crosswalk in `src/config.py`
   (mergers effective 2016: Dr Beyers Naude, Raymond Mhlaba, Enoch Mgijima, Walter Sisulu; 2000/2006 cross-boundary
   codes). Excluded: Umzimkulu (moved to KwaZulu-Natal in 2006) and District Management Areas. Matatiele joined the
   province in 2006, so 2000 has 32 municipalities.
4. Count registered voters and spoilt ballots once per voting district; sum party votes over rows.
5. Compute:
   - Turnout = 100 × (valid + spoilt) / registered
   - Party share = 100 × party votes / valid votes
   - Margin = largest share − second-largest share
   - ENP = 1 / Σ p_i² over the full party distribution (Laakso–Taagepera)
6. Validate against the IEC's official turnout reports and the earlier prototype.

## 2. Demographics (Notebook 02, `src/data/demographics.py`)

Two alignment policies, used for different jobs:

| Election | Descriptive (EDA) | As-known (models) |
|---|---|---|
| 2000, 2006 | missing | missing |
| 2011 | Census 2011 | missing (Census 2011 was taken after the May 2011 election) |
| 2016, 2021 | interpolated between Census 2011 and 2022 | Census 2011 |
| 2026 | – | Census 2022 |

## 3. Analysis of turnout (Notebook 03, `src/analysis/associations.py`)

- Turnout decomposition: Turnout = Level (unweighted provincial mean) + Relative position.
- Correlations reported **within each election** and year-demeaned across 2011–2021 (Fisher 95% intervals), alongside
  the pooled correlation to show where pooling misleads.
- OLS with election fixed effects, one pre-chosen variable per dimension (under-15 share, piped water, margin), standard
  errors clustered by municipality; variance inflation factors reported.
- Persistence of turnout and relative turnout between consecutive elections.
- Same-election competition measures are descriptive only and never used as predictors.

## 4. Turnout model (Notebook 04, `src/models/turnout.py`)

- **Target:** relative turnout position; full turnout is rebuilt by adding a provincial level.
- **Candidates:** provincial average (relative = 0), relative persistence, shrunk persistence, ridge regression and
  random forest on previous-election relative turnout, ENP, margin and log registered voters.
- **Validation:** rolling origin. Fold 2011 (train on 2006 target), fold 2016 (2006, 2011), fold 2021 (2006–2016).
- **Selection rule:** lowest mean MAE on the 2011 and 2016 folds, decided before the 2021 fold is inspected.
- **Supplementary:** a census-augmented model (Census 2011, as known) trained on 2016 and tested on 2021.
- **Error scale:** 80th percentile of absolute relative errors across all folds (3.79 points).

## 5. Party-support model (Notebook 05, `src/models/party.py`)

- Categories ANC, DA, EFF, UDM, ATM, OTHER; each modelled as a swing from its previous share.
- Candidates: no change, average swing, last swing, ridge regression, random forest.
- Same folds. Per party, lowest mean validation MAE among folds where the party already existed; otherwise "no change".
- Predictions clipped at zero and rescaled to 100% per municipality; evaluated per party, overall, and by largest party.

## 6. 2026 scenarios (Notebook 06, `src/models/scenarios.py`)

- **Turnout:** assumed provincial level + 2021 relative position (selected model). Levels: repeat of 2021 (48.0%),
  partial recovery (52.1%), return to 2016 (56.2%); any custom level in the dashboard. Band ±3.79 points (municipal
  pattern only).
- **Expected votes:** scenario turnout × registered voters (2021 placeholder until the 2026 registration file is added).
- **Party support:** selected methods refit on all transitions 2006–2021, applied to 2021 shares ("validated status
  quo"); alternative "trend continues" repeats each party's mean 2016→2021 swing (not validated). Optional uniform
  swings in the dashboard.
- **Too close to call:** lead smaller than twice the 2021 test MAE (5.37 points).
- **Swing needed:** half the leader's gap over the runner-up.

## Interpretation rules

Say "associated with", never "causes". Describe municipalities, not voters. Call 2026 values scenarios. Never present
error bands as confidence intervals.
