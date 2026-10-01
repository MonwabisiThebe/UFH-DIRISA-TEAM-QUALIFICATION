# Changes from the earlier prototype

The prototype (six `0N_phase*` notebooks) had a sound core: five-election reconstruction, voting-district
deduplication, PR-ballot consistency, an explicit crosswalk, ENP before grouping, demographic status flags, temporal
validation, baselines, ecological-inference warnings and QC gates. All of these are **kept**, moved into `src/` and
re-verified (Notebook 01 reproduces the prototype's cleaned election files exactly). The changes below correct
evaluation design, interpretation and provenance.

| # | Area | Prototype | Now | Why |
|---|---|---|---|---|
| 1 | Party model selection | Method per party chosen by its 2021 holdout error; that same error reported: MAE 2.502, 32/33 leaders | Methods chosen on validation folds 2011 and 2016; 2021 locked and evaluated once: **MAE 2.69, RMSE 4.02, 33/33** (no-change baseline 2.93, 33/33) | Selecting on the test set makes the reported error optimistic. The prototype's 32/33 was below the do-nothing baseline. |
| 2 | Turnout model selection | "Average Change Baseline" chosen by lowest 2021 MAE (7.725) | Rolling-origin validation selects **relative persistence**; locked 2021 result reported as two measures: **absolute 8.20**, **relative pattern 2.08 (r = 0.77)** | Same test-set issue; and the absolute error is dominated by a province-wide shock that no method anticipated. |
| 3 | Turnout target | Full turnout only | Turnout = provincial level + relative position; level becomes a stated scenario assumption | Separates what is predictable (municipal pattern) from what is not (provincial level). |
| 4 | Training data | 2006 transition unused | Expanding window uses 2006, 2011 and 2016 targets | More history, still time-ordered. |
| 5 | Associations | Pooled 2011–2021 correlations used to explain municipal differences | Two questions separated: across-election change (pooled, kept) and within-election differences (year-specific and year-demeaned r with 95% CIs; election fixed-effects regression) | Pooled correlations reverse sign for matric, higher education, no schooling, electricity, formal dwellings and ENP (Simpson's paradox). |
| 6 | Census in models | Interpolated values (using Census 2022) attached to 2016/2021 | Models use only censuses published before the election (Census 2011 for 2016/2021); interpolated values kept for description | Avoids using future information. Census 2011 added no out-of-sample value (reported as a finding). |
| 7 | External validation | None | Registered voters equal the IEC's official 2016/2021 reports in all 33 municipalities; turnout within 0.32 points; 2000–2011 province totals reconciled | Independent check on the reconstruction. |
| 8 | Province census file | `EC CENSUS.csv` described as provincial | Identified as a **Buffalo City** table (2022 total = BUF population) | Provenance correction. |
| 9 | `clean_census.csv` | Provenance unstated | Flagged as not verifiable from repository evidence | Transparency. |
| 10 | Map | None | 33-unit GeoJSON dissolved from MDB 2011 boundaries with the same crosswalk; validated against the analytical codes | Geography is central to the story. |
| 11 | Scenarios | Single central projection | Three named provincial-level assumptions (48.0 / 52.1 / 56.2%) + modelled relative pattern; validated status-quo and labelled trend alternative for parties; too-close-to-call rule; swing levers | Separates evidence from assumption. |
| 12 | Dashboard | Text-led, no map, decorative icon | Story flow (participation, competition, context, validation, scenarios, limitations) plus profiles, maps, scenario explorer calling the same `src` functions as Notebook 06, QC and downloads | One source of truth. |
| 13 | Housekeeping | Duplicate `2021/EC (2).xls`; outputs from phases mixed | Duplicate removed; prototype outputs moved to `data/processed/legacy_prototype/`; notebooks renamed by content | Clarity. |

Superseded headline numbers, kept here only for traceability: turnout MAE 7.725 (Average Change Baseline, selected on
2021), party MAE 2.502 with 32/33 leaders (selected on 2021). They must not appear elsewhere as results;
`src/validation/headline_metrics.py` scans the repository for them on every run.
