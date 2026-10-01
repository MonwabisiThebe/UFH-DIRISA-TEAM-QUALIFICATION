# Presentation script (15 minutes)

Aligned with `presentation/DIRISA_UFH_Presentation.pptx` (the same text is in each slide's speaker notes). Every number below is generated from the pipeline outputs; see `data/processed/verification/headline_metrics.csv`.

**Every member must present.** The script is split into four presenter blocks of roughly equal length. If the team has three members, merge blocks 3 and 4; if five, split block 2 at slide 9. Replace *Presenter 1-4* with names.

| Block | Slides | Topic | Approx. time |
|---|---|---|---|
| Presenter 1 | 1-5 | Problem, data, pipeline, IEC validation | 3:30 |
| Presenter 2 | 6-10 | Participation, maps, competition, two questions, associations | 3:50 |
| Presenter 3 | 11-14 | Persistence, validation design, turnout and party backtests | 3:50 |
| Presenter 4 | 15-19 | 2026 scenarios, dashboard, limitations, contribution | 3:40 |
| | | Total (excluding questions) | about 14:50; rehearse with a timer and trim slide 7 or 17 if over |

## Slide 1: Who turns out in the Eastern Cape, and what could 2026 look like?

*Presenter 1, about 0:35*

Good morning. We are a team from the University of Fort Hare. Our project asks two questions about the Eastern Cape: why does turnout differ so much between municipalities, and what do two decades of results suggest about the 2026 local elections? The map shows 2021 turnout; lighter municipalities voted more. Over the next fifteen minutes each of us presents one part: the problem and data, what we found, how we tested our models, and what it means for 2026.

## Slide 2: The problem

*Presenter 1, about 0:40*

Our research question is on the slide. The data to answer it exists, but it is fragmented: results files in different formats, separate turnout reports, a registration dashboard, and municipal boundaries that changed twice. Comparing a municipality across twenty years only works if every election is first put onto the same map. And because 2026 matters to many people, we wanted any statement about it to be honest about uncertainty.

## Slide 3: The data

*Presenter 1, about 0:45*

We rebuilt 164 municipality-elections from the raw IEC result files. Registered voters and spoilt ballots repeat on every party row, so we count them once per voting district. We use only the PR ballot, which every voter receives, so party support is comparable across elections. Older municipalities map onto today's 33 through an explicit crosswalk. Census indicators provide context; the exact upstream tables for our census file are not recorded in the repository, and we flag that openly.

## Slide 4: From raw files to dashboard: one reproducible pipeline

*Presenter 1, about 0:40*

The work runs as six notebooks in order, each writing the files the next one reads. The important engineering choice is that shared logic lives in one Python package, so the notebooks and the dashboard call the same code. One command rebuilds everything from the raw files in about a minute, runs nineteen validation checks and twenty-three tests, and writes every headline number to a single file so the slides, dashboard and documentation cannot disagree.

## Slide 5: Is the data right? Checked against the IEC's own figures

*Presenter 1, about 0:50*

Before analysing anything we checked our numbers against an independent source: the IEC's own turnout reports, which we did not use to build the data. Registered voters match exactly in all 33 municipalities in 2016 and 2021, and turnout agrees to about a third of a point. The small differences are definitional: the IEC also counts special votes and the larger of ward or PR ballots. Earlier province totals also reconcile exactly once excluded units are accounted for.

## Slide 6: Participation: a stable plateau, then a province-wide fall

*Presenter 2, about 0:45*

Turnout held between 56 and 58 percent for four elections. Then in 2021 it fell in every single municipality, by between four and eighteen points; the provincial mean dropped from 56 to 48 percent. When every municipality moves together, the cause is something province-wide or national, not local. The 2021 election took place during the pandemic. This observation shapes everything that follows: to understand differences between municipalities, we compare them within the same election.

## Slide 7: Where turnout is high and low has been remarkably consistent

*Presenter 2, about 0:35*

These five maps share one colour scale. Two things stand out: the whole province gets lighter in 2021, and the pattern of which municipalities are high or low hardly changes. Kouga and the western municipalities stay above the provincial level; King Sabata Dalindyebo and the eastern municipalities stay below. We built the map ourselves by dissolving official 2011 boundaries with the same crosswalk as the data, so the map and the numbers always agree.

## Slide 8: Competition: many more parties, a still-dominant ANC

*Presenter 2, about 0:40*

The ANC remains dominant, though its share has fallen since 2006. The EFF entered in 2016 and the ATM in 2021. The average municipal ballot went from about three parties to about ten, but the effective number of parties, which weights parties by their votes, rose only from 1.6 to 2.0. We compute it from every party before grouping small ones. Most contests are not close; Nelson Mandela Bay, decided by less than half a point, is the exception.

## Slide 9: Two questions: change over time vs differences between places

*Presenter 2, about 0:55*

This slide shows why the analysis must separate two questions. Coloured lines are individual elections: within each one, municipalities with more effective parties or more matric holders had higher turnout. The dashed line pools all three elections and slopes the other way, because 2021 combined lower turnout with more parties everywhere. The pooled view is a fair description of change over time, but the wrong tool for explaining why municipalities differ. Our prototype had mixed these up; we now answer each question separately.

## Slide 10: Within an election, context matters, but jointly

*Presenter 2, about 0:55*

Within each election, the pattern is consistent. Municipalities with a higher median age, better piped water and formal housing, and more matric holders had higher turnout; those with more children under fifteen and wider victory margins had lower turnout. Election year alone explains about half of all variation; these municipal characteristics take that to about 63 percent. But age structure, services and education move together geographically, so with 33 municipalities we cannot say which one matters. These are associations between places, not causes, and they say nothing about how individuals vote.

## Slide 11: The bridge to prediction: relative position persists

*Presenter 3, about 0:45*

Here is the key insight for prediction. We split each municipality's turnout into the provincial level plus its position relative to that level. The scatter shows 2016 position against 2021 position: it lies close to the diagonal, a correlation of 0.77, even though the whole province fell eight points in between. Since 2011, where a municipality sits relative to the province has been very stable. Before 2011 it was much noisier.

## Slide 12: How we tested: 2021 locked away until the very end

*Presenter 3, about 0:55*

To test honestly, we pretend to stand before each election. For the 2011 fold we train on 2006; for 2016 we train on 2006 and 2011. We choose the method with the lowest average error on those two validation folds. Only then do we look at 2021, once, and report whatever it gives. Then we refit the chosen method on all data through 2021 for the scenarios. Our earlier prototype picked models by their 2021 scores, which flatters the result; we fixed that, and accepted the less flattering numbers.

## Slide 13: Turnout: the pattern was predictable, the level was not

*Presenter 3, about 1:10*

We report two numbers for 2021, separately. The absolute turnout error was 8.2 points: every method, simple or machine learning, predicted turnout about eight points too high, because nothing in municipal history could foresee the province-wide fall. The relative-pattern error, which measures how well we captured differences between municipalities, was 2.08 points with a correlation of 0.77. Simple persistence won on validation and also on the locked test, beating ridge regression, random forests and the provincial-average baseline. Adding Census 2011 did not help. So: the provincial level was hard to anticipate, the municipal pattern was not.

## Slide 14: Party support: 'no change' is hard to beat

*Presenter 3, about 1:00*

For party support we model each party's swing. Validation chose 'no change' for the ANC, DA and UDM; the EFF and ATM did not exist in a validation fold, so they default to 'no change'; a random forest won for the OTHER category. On the locked 2021 test, the composite's error was 2.69 points against 2.93 for pure 'no change'. 'Last swing' would have helped the ANC but hurt the DA badly. All approaches identify the largest party in nearly every municipality, which tells us that leadership is easy to predict; the informative output is how close each contest is.

## Slide 15: 2026 turnout: one modelled pattern, three assumptions

*Presenter 4, about 0:50*

For 2026 we combine what the data validated with what it cannot tell us. The municipal pattern is modelled: each municipality keeps its 2021 position relative to the province, with a band of about 3.8 points from historical errors. The provincial level is an assumption, so we show three: a repeat of 2021 at 48 percent, partial recovery at 52, and a return to 2016 at 56. The maps differ only in overall shade. We do not claim any one of these is the forecast. Expected votes use 2021 registration until the 2026 IEC snapshot is added.

## Slide 16: 2026 party support: few contests are genuinely open

*Presenter 4, about 0:50*

Under the validated status-quo scenario the ANC has the largest share in 31 municipalities and the DA in 2. But the more useful question is how close each contest is. Nelson Mandela Bay's lead is under half a point, far inside our typical error of 2.7 points, so we call it too close to call. Dr Beyers Naude would change hands with a uniform swing of about 3.6 points; most other municipalities would need ten points or more. We do not model new parties, coalitions or the 2024 national election, which is why the dashboard lets users explore swings themselves.

## Slide 17: The dashboard: evidence and assumptions, clearly separated

*Presenter 4, about 0:45*

The dashboard follows the story of this talk: participation, competition, socioeconomic context, historical validation, 2026 scenarios and limitations, plus a profile for each municipality and CSV downloads. One design rule runs throughout: teal panels show validated evidence, orange panels mark assumptions. The scenario explorer calls exactly the same code as our final notebook, so the dashboard cannot drift from the analysis. [Optional: switch to a live demo here.]

## Slide 18: Limitations, and how we handled them

*Presenter 4, about 0:40*

We want to be clear about what this work cannot do. Five elections and 33 municipalities is a small sample. Our findings describe municipalities, not individual voters, and they are associations, not causes. The 2021 shock could not be anticipated, which is why the provincial level is an assumption. Merged municipalities are comparable but not identical over time. We could not verify the upstream tables of our census file, and there is no province-wide gender data; the 2026 registration snapshot is not yet extracted, but the pipeline is ready for it.

## Slide 19: What we contribute

*Presenter 4, about 0:35*

To close: we built a validated twenty-year municipal panel; we found that the provincial turnout level moves with events while each municipality's relative position is stable; we tested our models honestly with 2021 locked away; and we built a dashboard that separates evidence from assumption. Next we would add the 2026 registration data, try training only on the stable post-2011 period, and update everything after the November results. Thank you; we welcome your questions.

## Slide 20: References

*Not presented aloud*

Reference slide; not presented aloud. All web sources should be checked and access dates added before submission.

## Likely judge questions

**Why not a more complex model?** We tried ridge regression and random forests under the same validation; neither beat simple persistence for turnout, and only the OTHER party category benefited from a random forest. Complexity is not rewarded unless it generalises.

**Your 2021 turnout error is 8.2 points. Isn't that poor?** Yes, for absolute turnout, and every method shares it: the whole province fell by about 8 points. We report it alongside the 2.08-point relative-pattern error rather than replacing it, and we treat the 2026 provincial level as an explicit assumption.

**Why did your party numbers get worse than the earlier version?** The earlier version chose methods using 2021 itself. With 2021 locked away the honest error is 2.69 points (baseline 2.93).

**Does youth or gender affect turnout?** Municipalities with more children under 15 have lower turnout, but census data cannot tell us about the age or gender of voters. The IEC registration dashboard has age and gender; our pipeline is ready to ingest a 2026 extract.

**Where does your census file come from?** Its upstream tables are not recorded in the repository, and we say so; no headline result depends on it, and adding it did not improve forecasts.
