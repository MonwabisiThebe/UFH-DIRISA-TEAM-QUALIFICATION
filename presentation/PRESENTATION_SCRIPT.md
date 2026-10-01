# 15-Minute Presentation Script

## 1. Problem and motivation — 1:30
Introduce the Eastern Cape focus and research question. Explain that IEC data are rich but fragmented across elections and changing municipal geographies.

## 2. Data and harmonisation — 2:00
Show five LGE cycles, PR-ballot choice, municipality crosswalk, voting-district deduplication and Census context. Emphasise 164 municipality-election observations and explicit provenance.

## 3. Exploratory findings — 2:00
Show turnout trend and municipality variation, then competition measures (ENP and margin). State that demographic relationships are descriptive municipality-level associations, not causal individual-level claims.

## 4. Turnout model — 2:30
Explain temporal backtesting and leakage controls. Present the 2021 model comparison. Emphasise that Average Change Baseline had the lowest MAE (~7.725 pp), so the project retained it rather than choosing a more complex model. Mention weaker 2021 generalisation as a limitation.

## 5. Party-support model — 2:30
Explain party categories, swing target and category-specific method selection. Report overall reconstructed 2021 MAE (~2.502 pp) and 32/33 largest-share-category historical agreement as a diagnostic.

## 6. 2026 scenarios and dashboard — 2:30
Demonstrate the Streamlit municipality selector, history, context, model validation and scenario tabs. Explain sensitivity bands and stress that they are not confidence intervals or known outcomes.

## 7. Limitations and contribution — 1:30
Cover temporal instability, boundary harmonisation, limited cycles, new-party uncertainty, ecological interpretation and scenario uncertainty. Close on the contribution: one reproducible Eastern Cape pipeline linking raw election history, demographics, validation and an interactive deployment.

## Demo rule
Never describe a scenario as a certain result. Use phrases such as “the model-based scenario indicates”, “under the validated historical method”, and “the historical error sensitivity is…”.
