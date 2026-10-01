# Data sources and provenance

Raw files are never edited. Every processed file is written by a notebook and can be regenerated with
`python run_pipeline.py`. Citations below were compiled by the team: **check URLs and access dates before submission.**

## 1. IEC Local Government Election results (primary)

| Item | Detail |
|---|---|
| Publisher | Electoral Commission of South Africa (IEC) |
| Where | https://results.elections.org.za/home/downloads/me-results |
| Files | `data/raw/detailed/2000 LGE.csv`, `2006 LGE.csv`, `2011_detailed/EC.csv`, `2016_detailed/EC.csv`, `2021_detailed/EC.csv` |
| Granularity | One row per party × voting district × ballot type |
| Used for | Registered voters, votes cast, spoilt votes, PR party votes, turnout, ENP, margin |
| Notes | 2000/2006 files are national (filtered to Eastern Cape) with an older column layout; the 2011 file is UTF-16. Six malformed 2006 rows (a party name containing a comma) are all in Gauteng and do not affect this project. |

## 2. IEC Voter Turnout Reports (independent validation)

| Item | Detail |
|---|---|
| Files | `data/raw/turnout/2000 turnout.xls`, `2006_turnout.xls`, `2011_turnout.xls` (province level); `2016/EC.xls`, `2021/EC.xls` (municipality level) |
| Used for | Validation only, never as model input |
| Result | Registered voters match exactly for all 33 municipalities in 2016 and 2021 and for the province in 2011; 2000 differs by exactly the 55,674 voters of Umzimkulu (excluded: moved to KwaZulu-Natal in 2006); 2006 differs by 2,470 District Management Area voters (district ballot only). Turnout agrees within 0.32 points on average. |
| Definition difference | The IEC divides the larger of ward or PR votes cast by registered voters plus MEC7 special votes; the project uses PR votes cast over registered voters. |
| Housekeeping | A byte-identical duplicate, `2021/EC (2).xls`, was removed. |

## 3. Census municipal indicators (Statistics South Africa)

| Item | Detail |
|---|---|
| File | `data/processed/demographics/clean_census.csv` (33 rows; `<indicator>_2011` and `<indicator>_2022`) |
| Indicators | Population; % under 15; % 65+; median age; % adults with no schooling, matric, higher education; % households in formal dwellings, with piped water, with electricity |
| Origin | **Not recorded in the repository and not verifiable from repository evidence.** The indicators are Census-type municipal measures (Stats SA Census 2011 and 2022, https://census.statssa.gov.za, is the presumed but unconfirmed source). |
| Evidence available | Buffalo City's 2022 population (975,255) matches the Buffalo City census table below exactly. Its 2011 population differs (781,853 here against 755,200 in that table), so the 2011 basis is uncertain. |
| Status in analysis | Used as documented-but-unverified context in descriptive analysis and a supplementary model check only; no headline forecast depends on it. |
| **Team action** | If the person who built the file can identify the tables and download dates, record them here; otherwise keep this limitation statement. |

## 4. `data/external/demographics/EC CENSUS.csv`: a Buffalo City table, not provincial

Earlier documentation described this file as provincial. Its totals show it is a **Buffalo City Metropolitan Municipality**
age × sex × population-group table for Census 1996, 2001, 2011 and 2022: the 2022 total (975,255) equals Buffalo City's
2022 population exactly, whereas the Eastern Cape has roughly 7 million people. It is used only to illustrate that
municipal sex/age breakdowns exist (female share about 52.7%); it is not used as provincial evidence.

## 5. Municipal boundaries

| Item | Detail |
|---|---|
| File | `data/raw/geo/za-local.topojson` |
| Origin | Municipal Demarcation Board 2011 local-municipality boundaries, as redistributed by github.com/datawizzards/zadmaps (`geojson/za-local.topojson`) |
| Processing | The 39 Eastern Cape units are dissolved into the 33 analytical units with the project crosswalk (`src/data/geography.py`), producing `data/external/geo/ec_municipalities_33.geojson` |
| Caveats | Small non-merger boundary realignments made in 2016 are not represented; use for visual communication only. The redistribution repository has no explicit licence; the underlying data are MDB public boundaries. |

## 6. IEC Voter Registration Statistics (2026), optional

| Item | Detail |
|---|---|
| Where | https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics (dashboard; extract per municipality) |
| Expected file | `data/raw/registration/ec_registration_2026.csv` (template provided in the same folder) |
| Status | **Not yet collected.** Notebook 06 and the dashboard use 2021 registered voters as a labelled placeholder and switch automatically when the file is added. |

## 7. Legacy prototype outputs

`data/processed/legacy_prototype/` holds the earlier team prototype's cleaned files (`clean_res*.csv`,
`clean_competition*.csv`, `panel.csv`). They are not inputs; Notebook 01 confirms the rebuilt pipeline reproduces
them exactly.

## Methodological references

- Laakso, M. & Taagepera, R. (1979). "Effective" number of parties. *Comparative Political Studies*, 12(1), 3–27.
- Geys, B. (2006). Explaining voter turnout: a review of aggregate-level research. *Electoral Studies*, 25(4), 637–663.
- Robinson, W.S. (1950). Ecological correlations and the behavior of individuals. *American Sociological Review*, 15(3), 351–357.
- Simpson, E.H. (1951). The interpretation of interaction in contingency tables. *JRSS B*, 13(2), 238–241.
- Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.), section 5.10. https://otexts.com/fpp3/
- Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. *JMLR*, 12, 2825–2830.
- Seabold, S. & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. *Proc. SciPy*.
