# Limitations and how they were handled

| Limitation | Consequence | Mitigation |
|---|---|---|
| Five elections; 32–33 municipalities each | Few training transitions; low statistical power | Simple models and baselines; rolling-origin validation; report uncertainty |
| Boundary changes (2006 cross-boundary, 2016 mergers) | Harmonised units are comparable, not identical, over time | Explicit crosswalk; excluded units documented; same crosswalk for maps |
| 2021 election held during COVID-19 | Province-wide turnout shock no model could foresee | Turnout split into level (scenario assumption) and relative position (modelled) |
| Ecological data | Municipal associations do not describe individual voters | Language rules; no individual-level claims |
| Collinear municipal characteristics | Separate effects of age, services and competition cannot be isolated | Joint interpretation; VIFs reported; fixed-effects model |
| Census only in 2011 and 2022 | 2016/2021 values interpolated; no census before 2011 | Descriptive vs as-known policies; no future census in any backtest |
| `clean_census.csv` upstream tables not fully documented | Provenance gap | Flagged in DATA_SOURCES.md for the team to complete |
| No province-wide municipal gender or voter-age data | Gender and youth-registration questions cannot be answered | Listed as extension; registration hook ready |
| 2026 voter registration not yet extracted | Expected votes use 2021 registered voters | Placeholder clearly labelled; automatic switch when file added |
| New parties (EFF 2016, ATM 2021, post-2021 parties) | Cannot be learned from history | Default no-change rule; OTHER category; dashboard swing levers |
| No post-2021 electoral information (e.g. 2024 NPE, by-elections) | Scenarios start from 2021 | Stated in every scenario output |
| Map uses MDB 2011 boundaries dissolved to 33 units | Small 2016 realignments missing | Map used for communication only |
| Error bands are empirical | Not probabilistic intervals | Labelled as error scales throughout |
