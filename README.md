# Eastern Cape Municipal Electoral Dynamics

**University of Fort Hare | DIRISA Student Datathon Challenge 2026, Teams Qualification**

Two decades of Eastern Cape municipal election results, rebuilt from raw IEC files onto one consistent geography of
33 municipalities, analysed for what goes with higher or lower turnout, tested for whether turnout and party support
could have been predicted before the 2021 election, and turned into clearly labelled scenarios for the
4 November 2026 Local Government Elections, with an interactive dashboard.

## Problem statement

> **What explains differences in electoral participation across Eastern Cape municipalities, and what do historical
> electoral patterns suggest about turnout and party support in the 2026 Local Government Elections?**

**Why it matters.** The IEC publishes rich data, but it is spread across result downloads, turnout reports, dashboards
and changing municipal boundaries. Voters, journalists, civil society, parties and the IEC benefit from one coherent,
validated picture of where participation is weak, how persistent that is, and which municipal contests are genuinely
close, presented without overstating what the data can predict.

## Key findings

| | Finding | Evidence |
|---|---|---|
| 1 | **Turnout collapsed everywhere in 2021.** It held at 56–58% for four elections, then fell in all 33 municipalities (by 4.3 to 17.7 points; provincial mean 56.2% to 48.0%). | Notebook 03 |
| 2 | **Pooled correlations mislead.** Because 2021 combined lower turnout with more parties and better services everywhere, correlations that pool elections reverse sign for six variables (Simpson's paradox). | Notebook 03 |
| 3 | **Within each election, context matters.** Higher turnout goes with older age structure (median age r = +0.50; under-15 share r = −0.45), better services (piped water r = +0.47) and closer contests (margin r = −0.46). Election year alone explains 51% of turnout variation; these characteristics raise this to 63%, but overlap too much to separate. | Notebook 03 |
| 4 | **Relative turnout is predictable, the provincial level is not.** With 2021 locked as the test year, validation on 2011 and 2016 selected *relative persistence*. On 2021 its **absolute turnout error was 8.20 points** (every method missed the province-wide fall by about 8 points), while its **relative-pattern error was 2.08 points** (r = 0.77), better than ridge regression, random forests and the provincial-average baseline (2.98). | Notebook 04 |
| 5 | **Party support is mostly "no change".** Validation selects no-change for ANC, DA, UDM (and by rule EFF, ATM, which did not exist in a validation fold) and a random forest for OTHER. Locked 2021 test: MAE 2.69 points (RMSE 4.02) against 2.93 (4.47) for the no-change baseline; largest party correct in 33/33, as for the baseline. | Notebook 05 |
| 6 | **2026 scenarios, not forecasts.** Mean municipal turnout of 48.0%, 52.1% or 56.2% depending on the *assumed* provincial level (repeat of 2021, partial recovery, return to 2016), with each municipality's modelled relative position; ANC largest in 31 municipalities and DA in 2 under the status-quo scenario; **Nelson Mandela Bay is too close to call** (0.5-point gap). | Notebook 06 |

All relationships are municipality-level associations: not causal, and not statements about individual voters.

## Data

| Source | Use |
|---|---|
| IEC detailed LGE results 2000, 2006, 2011, 2016, 2021 (`data/raw/detailed/`) | Turnout, party shares, competition |
| IEC Voter Turnout Reports 2000–2021 (`data/raw/turnout/`) | Independent validation (registered voters match exactly) |
| Stats SA Census 2011 and 2022 municipal indicators (`data/processed/demographics/clean_census.csv`) | Demographic context |
| MDB 2011 municipal boundaries via github.com/datawizzards/zadmaps (`data/raw/geo/`) | Maps, dissolved with the project crosswalk |
| IEC Voter Registration Statistics 2026 (optional, `data/raw/registration/`) | Expected votes in scenarios (not yet collected) |

Full provenance and citations: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Repository layout

```
├── app/app.py                  Streamlit dashboard (10 pages)
├── data/
│   ├── raw/                    Unmodified inputs (IEC results, turnout reports, boundaries, registration)
│   ├── external/               Supporting inputs (Buffalo City census table, 33-unit GeoJSON)
│   └── processed/              Outputs written by the notebooks, one folder per phase
├── docs/                       Methodology, validation, sources, limitations, data dictionary, changes
├── notebooks/                  01-06: the analysis pipeline, run in order
├── presentation/               Slides (.pptx) and presenter script
├── reports/figures/            Figures saved by the notebooks (used in the slides)
├── src/                        Shared code: config, data, features, analysis, models, visualization, validation
├── submission/                 Submission checklist
├── tests/                      Unit, output-contract and dashboard tests
└── run_pipeline.py             Runs notebooks 01-06, the validator and the tests
```

## Run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python run_pipeline.py          # rebuild every output (about 1-2 minutes), validate, test, write verification report
streamlit run app/app.py        # open the dashboard
```

The notebooks can also be run one by one in Jupyter, in order 01 to 06. Details: [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Pipeline

| Notebook | Purpose | Main output |
|---|---|---|
| 01 Historical elections | Raw IEC files to a harmonised 164-row panel; IEC validation; map | `elections/phase1/municipality_election_panel_2000_2021.csv` |
| 02 Demographics | Census indicators; descriptive vs as-known alignment | `demographics/phase2/demographics_as_known_2000_2026.csv` |
| 03 Master panel and turnout analysis | Component A: associations within elections, regression, persistence | `panels/phase3/master_panel_2000_2021.csv` |
| 04 Turnout model | Rolling-origin backtest; level vs relative decomposition | `models/phase4/turnout_relative_scores.csv` |
| 05 Party-support model | Rolling-origin backtest per party; composition | `models/phase5/party_backtest_summary.csv` |
| 06 2026 scenarios | Validated patterns + stated assumptions | `scenarios/phase6/municipality_scenarios_2026.csv` |

## Methodological safeguards

- PR ballot only, so party support is measured on the same ballot every election.
- Registered voters and spoilt ballots counted once per voting district; validated against the IEC's own reports.
- Explicit municipality crosswalk; the same crosswalk builds the map.
- Effective number of parties computed from the full party distribution.
- Associations analysed within elections, not pooled.
- Rolling-origin validation; method selection never uses the 2021 test year.
- Census values enter models only if published before the election.
- 2026 outputs separate validated patterns from assumptions, and are labelled as scenarios.

Every headline number is generated into `data/processed/verification/headline_metrics.csv`, and
[`docs/VERIFICATION_REPORT.md`](docs/VERIFICATION_REPORT.md) records the latest end-to-end run.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md), [`docs/MODEL_VALIDATION.md`](docs/MODEL_VALIDATION.md),
[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) and [`docs/CHANGES_FROM_PROTOTYPE.md`](docs/CHANGES_FROM_PROTOTYPE.md).

## Software

Python 3.10+ with pandas, NumPy, Matplotlib, scikit-learn, statsmodels, Shapely, xlrd, Plotly and Streamlit
(versions in `requirements.txt`; each notebook also records the versions it ran with).
