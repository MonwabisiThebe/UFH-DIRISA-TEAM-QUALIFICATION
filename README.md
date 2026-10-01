# Eastern Cape Municipal Electoral Dynamics

**University of Fort Hare — DIRISA Student Datathon Challenge 2026**

This project studies municipal electoral participation, political competition and PR party-support patterns across the Eastern Cape using five Local Government Elections (2000, 2006, 2011, 2016 and 2021), municipality-level demographic context, historical model validation and explicitly labelled 2026 model-based scenarios.

## Research question
**What explains differences in electoral participation across Eastern Cape municipalities, and what do historical electoral patterns suggest about turnout and party support in the 2026 Local Government Elections?**

## Analytical design
The project is intentionally sequential and reproducible:
1. Historical IEC election reconstruction and municipality harmonisation.
2. Census demographic preparation and temporal alignment.
3. Master panel construction and exploratory analysis.
4. Leakage-safe turnout backtesting.
5. PR party-support backtesting.
6. Model-based 2026 scenarios with historical-error sensitivity.

The 2026 values are **scenarios, not known outcomes**. Methods are selected from historical validation rather than because they produce a preferred future result.

## Key validated findings
- Historical panel: **164 municipality-election observations** across five LGEs.
- Turnout: the **Average Change Baseline** has the lowest 2021 holdout MAE, about **7.725 percentage points**.
- Party support: reconstructed 2021 PR composition has overall MAE about **2.502 percentage points**; the largest-share historical category matches in **32/33 municipalities**.
- 2026 central turnout scenario: mean across 33 municipalities about **47.547%**, shown with historical-error sensitivity.

## Repository workflow
Run `notebooks/01_...` through `06_...` in order. Each phase writes versioned processed outputs used by the next phase. The Streamlit app reads those authoritative outputs directly and contains no dummy-data fallback.

## Run locally
```powershell
pip install -r requirements.txt
streamlit run app\app.py
```

## Methodological safeguards
- PR ballots are used consistently for party support.
- Registered voters/spoilt ballots are deduplicated at voting-district level where raw schemas repeat them.
- ENP is calculated from the full party distribution before selected-party grouping.
- Historical municipality changes are handled through an explicit crosswalk.
- Same-election outcomes are not used as pre-election turnout predictors.
- 2022-informed interpolated demographics are excluded from the strict pre-2021 turnout forecast.
- Temporal holdouts are used instead of random-row splits.

## Limitations
Historical relationships may change; 2021 was difficult to predict for turnout; party categories differ in predictability; new parties and structural political changes are difficult to infer from limited LGE cycles; municipality harmonisation cannot make historical boundaries perfectly identical; municipality-level associations do not identify individual voter behaviour; and MAE sensitivity bands are not confidence intervals.

See `docs/` for methodology, data sources, validation and limitations.
