// Builds presentation/DIRISA_UFH_Presentation.pptx from deck_data.json (run export_deck_data.py first).
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const HERE = __dirname;
const D = JSON.parse(fs.readFileSync(path.join(HERE, "deck_data.json"), "utf8"));
const REPO = path.resolve(HERE, "..", "..");

const INK = "1E2B2F", TEAL = "0E5E5A", TEAL_L = "7FB5AE", MIST = "EEF3F1", ALOE = "D2542B", GREY = "5C6B6E", PALE = "C9D6D4";
const PC = { ANC: "1B7A3E", DA: "1F5AA6", EFF: "A11D33", UDM: "E0A526", ATM: "6B4C9A", OTHER: "8C8C8C" };
const PARTIES = ["ANC", "DA", "EFF", "UDM", "ATM", "OTHER"];
const HF = "Cambria", BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Eastern Cape Municipal Electoral Dynamics";
pres.author = "University of Fort Hare team";

const W = 13.333, M = 0.6;

function title(s, text, sub) {
  s.addText(text, { x: M, y: 0.4, w: W - 2 * M, h: 0.85, fontFace: HF, fontSize: 30, bold: true, color: INK, margin: 0, isTextBox: true, valign: "top" });
  if (sub) s.addText(sub, { x: M, y: 1.22, w: W - 2 * M, h: 0.45, fontFace: BF, fontSize: 15, color: GREY, margin: 0, isTextBox: true });
}
function tag(s, kind) {
  const ev = kind === "evidence";
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: W - M - 2.2, y: 6.98, w: 2.2, h: 0.34, rectRadius: 0.17,
    fill: { color: ev ? MIST : "FBEDE7" }, line: { color: ev ? TEAL : ALOE, width: 1 } });
  s.addText(ev ? "Validated evidence" : "Scenario assumption", { x: W - M - 2.2, y: 6.98, w: 2.2, h: 0.34, fontFace: BF, fontSize: 11,
    bold: true, color: ev ? TEAL : ALOE, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
function stat(s, x, y, w, big, label, color) {
  s.addText(big, { x, y, w, h: 0.8, fontFace: HF, fontSize: 40, bold: true, color: color || TEAL, margin: 0, isTextBox: true });
  s.addText(label, { x, y: y + 0.82, w, h: 0.75, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true, valign: "top" });
}
function body(s, x, y, w, h, runs, size) {
  s.addText(runs, { x, y, w, h, fontFace: BF, fontSize: size || 15, color: INK, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 8 });
}
function bullets(items) { return items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })); }
function source(s, text) {
  s.addText(text, { x: M, y: 7.0, w: W - 2 * M, h: 0.3, fontFace: BF, fontSize: 10, color: GREY, margin: 0, isTextBox: true });
}
function card(s, x, y, w, h, fill) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill || MIST }, line: { color: fill || MIST } }); }
const axis = { catAxisLabelColor: GREY, valAxisLabelColor: GREY, valGridLine: { color: "E3E9E8", size: 0.5 }, catGridLine: { style: "none" },
  catAxisLabelFontFace: BF, valAxisLabelFontFace: BF, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, titleFontFace: HF, titleColor: INK, titleFontSize: 14 };

// 1. Title -------------------------------------------------------------------
let s = pres.addSlide(); s.background = { color: INK };
s.addImage({ path: path.join(HERE, "title_map.png"), x: 6.6, y: 1.5, w: 6.2, h: 6.2 * 700 / 1240 });
s.addText("Who turns out in the Eastern Cape, and what could 2026 look like?", { x: M, y: 1.3, w: 6.2, h: 2.6, fontFace: HF, fontSize: 38, bold: true, color: "FFFFFF", margin: 0, isTextBox: true, valign: "top" });
s.addText("Municipal electoral dynamics, Local Government Elections 2000 to 2021, with 2026 scenarios", { x: M, y: 4.1, w: 5.8, h: 0.9, fontFace: BF, fontSize: 17, color: TEAL_L, margin: 0, isTextBox: true });
s.addText("University of Fort Hare team  |  DIRISA Student Datathon Challenge 2026, Teams Qualification", { x: M, y: 6.5, w: 9, h: 0.4, fontFace: BF, fontSize: 13, color: "B8C4C2", margin: 0, isTextBox: true });
s.addText("Map: 2021 turnout by municipality (lighter = higher)", { x: 6.6, y: 5.2, w: 6.2, h: 0.3, fontFace: BF, fontSize: 10, color: "8FA3A0", margin: 0, isTextBox: true, align: "right" });
s.addNotes("[Presenter 1] Good morning. We are a team from the University of Fort Hare. Our project asks two questions about the Eastern Cape: why does turnout differ so much between municipalities, and what do two decades of results suggest about the 2026 local elections? The map shows 2021 turnout; lighter municipalities voted more. Over the next fifteen minutes each of us presents one part: the problem and data, what we found, how we tested our models, and what it means for 2026.");

// 2. Problem ------------------------------------------------------------------
s = pres.addSlide(); title(s, "The problem", "Rich public data, but no single validated picture of municipal participation");
card(s, M, 1.95, 6.9, 2.6, MIST);
s.addText("What explains differences in electoral participation across Eastern Cape municipalities, and what do historical patterns suggest about turnout and party support in the 2026 Local Government Elections?",
  { x: M + 0.35, y: 2.15, w: 6.2, h: 2.2, fontFace: HF, fontSize: 20, italic: true, color: TEAL, margin: 0, isTextBox: true, valign: "middle" });
body(s, M, 4.9, 6.9, 1.9, bullets([
  "IEC data is spread across result downloads, turnout reports and dashboards",
  "Municipal boundaries changed in 2006 and 2016, so places must be harmonised before comparing",
  "Forecasts are only useful if their uncertainty is honest"]), 15);
s.addText("Who benefits", { x: 8.1, y: 1.95, w: 4.6, h: 0.45, fontFace: HF, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true });
const who = [["Voters and civil society", "where participation is weakest"], ["Journalists", "which contests are genuinely close"], ["The IEC and parties", "where turnout outreach matters most"], ["Researchers", "a reproducible, validated municipal panel"]];
who.forEach((w_, i) => {
  const y = 2.6 + i * 1.05;
  s.addShape(pres.shapes.OVAL, { x: 8.1, y: y + 0.08, w: 0.42, h: 0.42, fill: { color: TEAL }, line: { color: TEAL } });
  s.addText(String(i + 1), { x: 8.1, y: y + 0.08, w: 0.42, h: 0.42, fontFace: BF, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText([{ text: w_[0], options: { bold: true, breakLine: true } }, { text: w_[1], options: { color: GREY } }], { x: 8.7, y, w: 4.0, h: 0.85, fontFace: BF, fontSize: 15, color: INK, margin: 0, isTextBox: true, valign: "top" });
});
s.addNotes("[Presenter 1] Our research question is on the slide. The data to answer it exists, but it is fragmented: results files in different formats, separate turnout reports, a registration dashboard, and municipal boundaries that changed twice. Comparing a municipality across twenty years only works if every election is first put onto the same map. And because 2026 matters to many people, we wanted any statement about it to be honest about uncertainty.");

// 3. Data -----------------------------------------------------------------------
s = pres.addSlide(); title(s, "The data", "Five elections rebuilt from raw IEC files onto one geography of 33 municipalities"); tag(s, "evidence");
stat(s, M, 1.95, 2.8, String(D.nobs), "municipality-elections (32 in 2000, 33 after)");
stat(s, M + 3.0, 1.95, 2.8, D.vd.toLocaleString("en-US"), "voting districts in 2021, deduplicated");
stat(s, M + 6.0, 1.95, 2.8, "5", "Local Government Elections, 2000 to 2021");
stat(s, M + 9.0, 1.95, 2.8, "33", "present-day municipalities via explicit crosswalk");
const rows = [
  [{ text: "Source", options: { bold: true, color: "FFFFFF", fill: { color: TEAL } } }, { text: "Role", options: { bold: true, color: "FFFFFF", fill: { color: TEAL } } }],
  ["IEC detailed LGE results 2000-2021 (PR ballot)", "Turnout, party shares, competition"],
  ["IEC Voter Turnout Reports 2000-2021", "Independent validation only"],
  ["Census 2011 and 2022 municipal indicators", "Demographic context (provenance flagged)"],
  ["MDB 2011 boundaries, dissolved with our crosswalk", "Maps on exactly the same 33 units"],
  ["IEC 2026 registration snapshot", "Optional: pipeline ready, not yet collected"]];
s.addTable(rows, { x: M, y: 3.85, w: W - 2 * M, colW: [6.4, 5.73], fontFace: BF, fontSize: 13, color: INK, border: { type: "solid", color: "D5DEDC", pt: 0.75 }, rowH: 0.42, fill: { color: "FFFFFF" } });
s.addNotes("[Presenter 1] We rebuilt 164 municipality-elections from the raw IEC result files. Registered voters and spoilt ballots repeat on every party row, so we count them once per voting district. We use only the PR ballot, which every voter receives, so party support is comparable across elections. Older municipalities map onto today's 33 through an explicit crosswalk. Census indicators provide context; the exact upstream tables for our census file are not recorded in the repository, and we flag that openly.");

// 4. Pipeline -------------------------------------------------------------------
s = pres.addSlide(); title(s, "From raw files to dashboard: one reproducible pipeline", "python run_pipeline.py rebuilds every number, then validates and tests");
const steps = [["01", "Historical elections", "harmonise, deduplicate, IEC check, map"], ["02", "Demographics", "descriptive vs as-known census"], ["03", "Analysis", "within-election associations, persistence"],
  ["04", "Turnout model", "rolling-origin validation, 2021 locked"], ["05", "Party model", "same design per party"], ["06", "2026 scenarios", "validated pattern + stated assumption"]];
steps.forEach((st_, i) => {
  const x = M + i * 2.04;
  card(s, x, 2.0, 1.86, 2.55, i < 3 ? MIST : (i < 5 ? "E1ECEA" : "FBEDE7"));
  s.addText(st_[0], { x: x + 0.15, y: 2.12, w: 1.6, h: 0.55, fontFace: HF, fontSize: 24, bold: true, color: i === 5 ? ALOE : TEAL, margin: 0, isTextBox: true });
  s.addText(st_[1], { x: x + 0.15, y: 2.7, w: 1.6, h: 0.6, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true, valign: "top" });
  s.addText(st_[2], { x: x + 0.15, y: 3.35, w: 1.6, h: 1.1, fontFace: BF, fontSize: 12, color: GREY, margin: 0, isTextBox: true, valign: "top" });
});
s.addText("Safeguards kept from the prototype and strengthened", { x: M, y: 4.95, w: 7, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: INK, margin: 0, isTextBox: true });
body(s, M, 5.45, 6.0, 1.5, bullets(["Voting-district deduplication; PR-ballot consistency", "Effective number of parties before grouping small parties", "Quality-control gates stop any notebook that fails"]), 14);
body(s, 6.9, 5.45, 5.8, 1.5, bullets(["Time-ordered validation, never random splits", "Shared code in src/ used by notebooks and dashboard", "23 automated tests; every headline number generated to one file"]), 14);
s.addNotes("[Presenter 1] The work runs as six notebooks in order, each writing the files the next one reads. The important engineering choice is that shared logic lives in one Python package, so the notebooks and the dashboard call the same code. One command rebuilds everything from the raw files in about a minute, runs nineteen validation checks and twenty-three tests, and writes every headline number to a single file so the slides, dashboard and documentation cannot disagree.");

// 5. External validation ---------------------------------------------------------
s = pres.addSlide(); title(s, "Is the data right? Checked against the IEC's own figures", "Our reconstruction vs the IEC's official 2016 and 2021 turnout reports"); tag(s, "evidence");
const sc16 = D.iec["2016"], sc21 = D.iec["2021"];
s.addChart(pres.charts.SCATTER, [{ name: "X", values: sc16.x.concat(sc21.x) }, { name: "2016", values: sc16.y.concat(sc21.x.map(() => null)) }, { name: "2021", values: sc16.x.map(() => null).concat(sc21.y) }],
  { x: M, y: 1.85, w: 6.6, h: 4.8, ...axis, chartColors: [TEAL, ALOE], lineSize: 0, lineDataSymbolSize: 7, showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 12,
    valAxisMinVal: 38, valAxisMaxVal: 70, catAxisMinVal: 38, catAxisMaxVal: 70, valAxisMajorUnit: 8, catAxisMajorUnit: 8, showValAxisTitle: true, valAxisTitle: "Reconstructed turnout (%)", showCatAxisTitle: true, catAxisTitle: "Official IEC turnout (%)",
    valAxisTitleFontSize: 12, catAxisTitleFontSize: 12, valAxisTitleColor: GREY, catAxisTitleColor: GREY });
stat(s, 7.7, 2.0, 5.0, "33 of 33", "municipalities with registered voters exactly equal to the IEC, in both 2016 and 2021");
stat(s, 7.7, 3.7, 5.0, `${sc16.mad} / ${sc21.mad} pts`, "mean turnout gap (2016 / 2021): the IEC also counts special votes and ward ballots");
body(s, 7.7, 5.4, 5.0, 1.4, [{ text: "Province totals 2000 to 2011 reconcile too: ", options: { bold: true } }, { text: "the 2000 gap is exactly Umzimkulu's 55,674 voters (moved to KwaZulu-Natal) and 2006's 2,470 are District Management Area voters." }], 14);
s.addNotes("[Presenter 1] Before analysing anything we checked our numbers against an independent source: the IEC's own turnout reports, which we did not use to build the data. Registered voters match exactly in all 33 municipalities in 2016 and 2021, and turnout agrees to about a third of a point. The small differences are definitional: the IEC also counts special votes and the larger of ward or PR ballots. Earlier province totals also reconcile exactly once excluded units are accounted for.");

// 6. Participation ---------------------------------------------------------------
s = pres.addSlide(); title(s, "Participation: a stable plateau, then a province-wide fall", "Provincial turnout, Local Government Elections 2000 to 2021"); tag(s, "evidence");
s.addChart(pres.charts.LINE, [{ name: "Municipal mean", labels: D.years, values: D.mean }, { name: "Registered-voter weighted", labels: D.years, values: D.wt }, { name: "Lowest municipality", labels: D.years, values: D.minT }, { name: "Highest municipality", labels: D.years, values: D.maxT }],
  { x: M, y: 1.85, w: 7.6, h: 4.8, ...axis, chartColors: [TEAL, ALOE, PALE, PALE], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 8, valAxisMinVal: 35, valAxisMaxVal: 70,
    showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 12, showValAxisTitle: true, valAxisTitle: "Turnout (%)", valAxisTitleColor: GREY, valAxisTitleFontSize: 12,
    showValue: false });
stat(s, 8.7, 2.0, 4.0, `${D.chg.n} of 33`, "municipalities had lower turnout in 2021 than in 2016");
stat(s, 8.7, 3.65, 4.0, `${D.chg.min} to ${D.chg.max}`, `points: the range of falls (mean ${D.chg.mean})`);
body(s, 8.7, 5.3, 4.0, 1.5, [{ text: "A fall that hits every municipality is a province-wide shock. ", options: { bold: true } }, { text: "The 2021 election was held during COVID-19. Differences between municipalities must be studied within each election." }], 14);
s.addNotes("[Presenter 2] Turnout held between 56 and 58 percent for four elections. Then in 2021 it fell in every single municipality, by between four and eighteen points; the provincial mean dropped from 56 to 48 percent. When every municipality moves together, the cause is something province-wide or national, not local. The 2021 election took place during the pandemic. This observation shapes everything that follows: to understand differences between municipalities, we compare them within the same election.");

// 7. Maps ------------------------------------------------------------------------
s = pres.addSlide(); title(s, "Where turnout is high and low has been remarkably consistent", "Turnout by municipality, same colour scale for all five elections"); tag(s, "evidence");
s.addImage({ path: path.join(HERE, "maps5.png"), x: M, y: 2.0, w: W - 2 * M, h: (W - 2 * M) * 432 / 2500 });
body(s, M, 4.75, 5.9, 1.5, bullets(["Western Karoo, coastal and metro municipalities sit above the provincial level", "The east (O.R. Tambo, Alfred Nzo) sits below, and lowest in 2021 is King Sabata Dalindyebo (39.4%)"]), 14);
body(s, 6.9, 4.75, 5.8, 1.5, bullets(["Map built by dissolving MDB 2011 boundaries with the same crosswalk as the data", "All 33 map units validated against the analytical codes"]), 14);
s.addNotes("[Presenter 2] These five maps share one colour scale. Two things stand out: the whole province gets lighter in 2021, and the pattern of which municipalities are high or low hardly changes. Kouga and the western municipalities stay above the provincial level; King Sabata Dalindyebo and the eastern municipalities stay below. We built the map ourselves by dissolving official 2011 boundaries with the same crosswalk as the data, so the map and the numbers always agree.");

// 8. Competition -------------------------------------------------------------------
s = pres.addSlide(); title(s, "Competition: many more parties, a still-dominant ANC", "Provincial PR vote share, and parties per municipality"); tag(s, "evidence");
s.addChart(pres.charts.BAR, PARTIES.map(p => ({ name: p, labels: D.years, values: D.prov[p] })),
  { x: M, y: 1.85, w: 6.6, h: 4.8, barDir: "col", barGrouping: "stacked", ...axis, chartColors: PARTIES.map(p => PC[p]), valAxisMaxVal: 100, showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 11,
    showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF", dataLabelFontSize: 9, dataLabelFormatCode: "0;;;", showTitle: true, title: "PR vote share (%)" });
s.addChart(pres.charts.LINE, [{ name: "Parties contesting (mean)", labels: D.years, values: D.parties }, { name: "Effective number of parties (mean)", labels: D.years, values: D.enp }],
  { x: 7.5, y: 1.85, w: 5.2, h: 3.3, ...axis, chartColors: [INK, TEAL], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 7, showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 11, showTitle: true, title: "More parties, modest fragmentation" });
body(s, 7.5, 5.35, 5.2, 1.5, [{ text: "Parties on the ballot tripled, but the effective number rose only from 1.6 to 2.0: ", options: { bold: true } }, { text: "most new parties win small shares. Nelson Mandela Bay was decided by 0.44 points in 2021." }], 14);
s.addNotes("[Presenter 2] The ANC remains dominant, though its share has fallen since 2006. The EFF entered in 2016 and the ATM in 2021. The average municipal ballot went from about three parties to about ten, but the effective number of parties, which weights parties by their votes, rose only from 1.6 to 2.0. We compute it from every party before grouping small ones. Most contests are not close; Nelson Mandela Bay, decided by less than half a point, is the exception.");

// 9. Two questions ---------------------------------------------------------------------
s = pres.addSlide(); title(s, "Two questions: change over time vs differences between places", "Turnout against effective number of parties and matric attainment, 2011 to 2021"); tag(s, "evidence");
s.addImage({ path: REPO + "/reports/figures/phase3/simpsons_paradox.png", x: M, y: 1.85, w: 8.3, h: 8.3 * 950 / 2477 });
card(s, 9.2, 1.85, 3.53, 4.9, MIST);
body(s, 9.45, 2.05, 3.1, 4.6, [
  { text: "Across elections", options: { bold: true, color: TEAL, breakLine: true } },
  { text: "Turnout fell while parties and service levels rose. The pooled dashed line describes that co-movement.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true } },
  { text: "Within an election", options: { bold: true, color: TEAL, breakLine: true } },
  { text: "Municipalities with more parties or more matric holders had higher turnout. Pooling reverses the sign for six variables (Simpson's paradox)." }], 14);
body(s, M, 5.25, 8.3, 1.5, [{ text: "We keep both views but answer each question with the right one: ", options: { bold: true } }, { text: "provincial trends for change over time; year-specific and year-demeaned correlations for differences between municipalities." }], 14);
s.addNotes("[Presenter 2] This slide shows why the analysis must separate two questions. Coloured lines are individual elections: within each one, municipalities with more effective parties or more matric holders had higher turnout. The dashed line pools all three elections and slopes the other way, because 2021 combined lower turnout with more parties everywhere. The pooled view is a fair description of change over time, but the wrong tool for explaining why municipalities differ. Our prototype had mixed these up; we now answer each question separately.");

// 10. Within-election associations ------------------------------------------------------
s = pres.addSlide(); title(s, "Within an election, context matters, but jointly", "Correlation with turnout, 2011 to 2021, after removing election-year differences"); tag(s, "evidence");
s.addChart(pres.charts.BAR, [{ name: "Within-election r", labels: D.assoc.labels, values: D.assoc.within }],
  { x: M, y: 1.85, w: 7.3, h: 4.8, barDir: "bar", ...axis, chartColors: [TEAL], valAxisMinVal: -0.6, valAxisMaxVal: 0.6, showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelFormatCode: "+0.00;-0.00", dataLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelPos: "low", valAxisLabelFormatCode: "0.0", valAxisMajorUnit: 0.2 });
stat(s, 8.4, 2.0, 4.3, `${Math.round(D.r2[0] * 100)}%`, "of turnout variation explained by election year alone (2011 to 2021)");
stat(s, 8.4, 3.65, 4.3, `${Math.round(D.r2[1] * 100)}%`, "with age structure, piped water and victory margin added (election fixed effects)");
body(s, 8.4, 5.3, 4.3, 1.5, [{ text: "Older, better-serviced municipalities and closer contests go with higher turnout. ", options: { bold: true } }, { text: "These overlap too much to separate with 33 municipalities. Associations only, not causes." }], 13);
s.addNotes("[Presenter 2] Within each election, the pattern is consistent. Municipalities with a higher median age, better piped water and formal housing, and more matric holders had higher turnout; those with more children under fifteen and wider victory margins had lower turnout. Election year alone explains about half of all variation; these municipal characteristics take that to about 63 percent. But age structure, services and education move together geographically, so with 33 municipalities we cannot say which one matters. These are associations between places, not causes, and they say nothing about how individuals vote.");

// 11. Persistence ---------------------------------------------------------------------------
s = pres.addSlide(); title(s, "The bridge to prediction: relative position persists", "Points above or below the provincial level, 2016 against 2021"); tag(s, "evidence");
s.addChart(pres.charts.SCATTER, [{ name: "X", values: D.relscatter.x }, { name: "Municipalities", values: D.relscatter.y }],
  { x: M, y: 1.85, w: 6.0, h: 4.8, ...axis, chartColors: [TEAL], lineSize: 0, lineDataSymbolSize: 8, showLegend: false, valAxisMinVal: -12, valAxisMaxVal: 12, catAxisMinVal: -12, catAxisMaxVal: 12,
    valAxisMajorUnit: 4, catAxisMajorUnit: 4, valAxisLabelPos: "low", catAxisLabelPos: "low",
    showValAxisTitle: true, valAxisTitle: "2021 relative turnout (pts)", showCatAxisTitle: true, catAxisTitle: "2016 relative turnout (pts)", valAxisTitleColor: GREY, catAxisTitleColor: GREY, valAxisTitleFontSize: 12, catAxisTitleFontSize: 12 });
s.addChart(pres.charts.BAR, [{ name: "r", labels: D.persist.labels, values: D.persist.r }],
  { x: 7.0, y: 1.85, w: 5.7, h: 3.2, barDir: "col", ...axis, chartColors: [TEAL_L], valAxisMinVal: 0, valAxisMaxVal: 1, showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelColor: INK, showTitle: true, title: "Correlation of relative position, election to election" });
body(s, 7.0, 5.3, 5.7, 1.5, [{ text: "Turnout = provincial level + relative position. ", options: { bold: true } }, { text: "Since 2011 the relative position carries over strongly (r = 0.83, then 0.77) even as the level fell 8 points." }], 14);
s.addNotes("[Presenter 3] Here is the key insight for prediction. We split each municipality's turnout into the provincial level plus its position relative to that level. The scatter shows 2016 position against 2021 position: it lies close to the diagonal, a correlation of 0.77, even though the whole province fell eight points in between. Since 2011, where a municipality sits relative to the province has been very stable. Before 2011 it was much noisier.");

// 12. Validation design -----------------------------------------------------------------------
s = pres.addSlide(); title(s, "How we tested: 2021 locked away until the very end", "Rolling-origin validation; method chosen before 2021 is examined; no random splits"); tag(s, "evidence");
const yrs = ["2006", "2011", "2016", "2021"], folds = [["2011", ["2006"], "Validation"], ["2016", ["2006", "2011"], "Validation"], ["2021", ["2006", "2011", "2016"], "Locked test"]];
yrs.forEach((y, j) => s.addText(y, { x: 2.7 + j * 1.75, y: 1.95, w: 1.6, h: 0.35, fontFace: BF, fontSize: 13, bold: true, color: GREY, align: "center", margin: 0, isTextBox: true }));
folds.forEach((f, i) => {
  const y = 2.4 + i * 0.75;
  s.addText(`Fold ${f[0]}`, { x: M, y, w: 1.9, h: 0.6, fontFace: BF, fontSize: 14, bold: true, color: INK, valign: "middle", margin: 0, isTextBox: true });
  yrs.forEach((yy, j) => {
    const train = f[1].includes(yy), tgt = yy === f[0];
    const fill = train ? TEAL_L : tgt ? (f[2] === "Locked test" ? ALOE : TEAL) : "F2F5F4";
    s.addShape(pres.shapes.RECTANGLE, { x: 2.7 + j * 1.75, y, w: 1.6, h: 0.6, fill: { color: fill }, line: { color: "FFFFFF" } });
    if (train || tgt) s.addText(train ? "train" : (f[2] === "Locked test" ? "TEST" : "validate"), { x: 2.7 + j * 1.75, y, w: 1.6, h: 0.6, fontFace: BF, fontSize: 13, bold: true, color: train ? INK : "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
});
const proto = [["1", "Choose", "lowest mean error on folds 2011 and 2016 only"], ["2", "Freeze", "method fixed before looking at 2021"], ["3", "Test once", "report 2021 error, good or bad"], ["4", "Refit", "same method on all data through 2021 for 2026"]];
proto.forEach((p, i) => {
  const x = M + i * 3.07;
  card(s, x, 4.95, 2.85, 1.8, MIST);
  s.addText(p[0], { x: x + 0.2, y: 5.05, w: 0.6, h: 0.6, fontFace: HF, fontSize: 26, bold: true, color: TEAL, margin: 0, isTextBox: true });
  s.addText(p[1], { x: x + 0.8, y: 5.12, w: 1.9, h: 0.45, fontFace: BF, fontSize: 16, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText(p[2], { x: x + 0.2, y: 5.7, w: 2.5, h: 0.95, fontFace: BF, fontSize: 13, color: GREY, margin: 0, isTextBox: true, valign: "top" });
});
s.addText("Our earlier prototype chose its models by their 2021 scores. We corrected this: choosing on the test year makes the reported error optimistic.", { x: 8.0, y: 2.45, w: 4.7, h: 2.0, fontFace: BF, fontSize: 14, italic: true, color: ALOE, margin: 0, isTextBox: true, valign: "top" });
s.addNotes("[Presenter 3] To test honestly, we pretend to stand before each election. For the 2011 fold we train on 2006; for 2016 we train on 2006 and 2011. We choose the method with the lowest average error on those two validation folds. Only then do we look at 2021, once, and report whatever it gives. Then we refit the chosen method on all data through 2021 for the scenarios. Our earlier prototype picked models by their 2021 scores, which flatters the result; we fixed that, and accepted the less flattering numbers.");

// 13. Turnout result ------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "Turnout: the pattern was predictable, the level was not", "Error in predicting relative turnout (points), by method"); tag(s, "evidence");
s.addChart(pres.charts.BAR, [{ name: "Mean validation (2011, 2016)", labels: D.turn.labels, values: D.turn.val }, { name: "2021 locked test", labels: D.turn.labels, values: D.turn.test }],
  { x: M, y: 1.85, w: 7.2, h: 4.8, barDir: "bar", barGrouping: "clustered", ...axis, chartColors: [PALE, TEAL], valAxisMinVal: 0, valAxisMaxVal: 4, showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 12,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelColor: INK, dataLabelFontSize: 10, catAxisOrientation: "maxMin" });
card(s, 8.2, 1.9, 4.5, 2.25, "FBEDE7");
s.addText(`${D.abs.mae.toFixed(2)} pts`, { x: 8.45, y: 2.0, w: 4.0, h: 0.75, fontFace: HF, fontSize: 36, bold: true, color: ALOE, margin: 0, isTextBox: true });
s.addText("Absolute turnout error, 2021. Includes the province-wide fall: predictions were 8.2 points too high, as for every method.", { x: 8.45, y: 2.8, w: 4.0, h: 1.25, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true, valign: "top" });
card(s, 8.2, 4.45, 4.5, 2.3, MIST);
s.addText(`${D.relt.mae.toFixed(2)} pts`, { x: 8.45, y: 4.55, w: 4.0, h: 0.75, fontFace: HF, fontSize: 36, bold: true, color: TEAL, margin: 0, isTextBox: true });
s.addText(`Relative-pattern error, 2021 (r = ${D.relt.r}). Relative persistence won validation and also won the locked test; Census 2011 added nothing.`, { x: 8.45, y: 5.35, w: 4.0, h: 1.3, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true, valign: "top" });
s.addNotes("[Presenter 3] We report two numbers for 2021, separately. The absolute turnout error was 8.2 points: every method, simple or machine learning, predicted turnout about eight points too high, because nothing in municipal history could foresee the province-wide fall. The relative-pattern error, which measures how well we captured differences between municipalities, was 2.08 points with a correlation of 0.77. Simple persistence won on validation and also on the locked test, beating ridge regression, random forests and the provincial-average baseline. Adding Census 2011 did not help. So: the provincial level was hard to anticipate, the municipal pattern was not.");

// 14. Party result ---------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "Party support: 'no change' is hard to beat", "2021 locked-test error by party (percentage points of vote share)"); tag(s, "evidence");
const sel = D.party["Selected by validation (used for 2026)"], nc = D.party["No change for every party (baseline)"], ls = D.party["Last swing for every party (trend continues)"];
s.addChart(pres.charts.BAR, [{ name: `Selected (overall ${sel.mae.toFixed(2)})`, labels: PARTIES, values: sel.per }, { name: `No change (${nc.mae.toFixed(2)})`, labels: PARTIES, values: nc.per }, { name: `Last swing (${ls.mae.toFixed(2)})`, labels: PARTIES, values: ls.per }],
  { x: M, y: 1.85, w: 7.6, h: 4.8, barDir: "col", barGrouping: "clustered", ...axis, chartColors: [TEAL, PALE, ALOE], showLegend: true, legendPos: "b", legendFontFace: BF, legendFontSize: 12, valAxisMinVal: 0,
    showValAxisTitle: true, valAxisTitle: "MAE (pts)", valAxisTitleColor: GREY, valAxisTitleFontSize: 12 });
stat(s, 8.6, 2.0, 4.1, `${sel.mae.toFixed(2)} vs ${nc.mae.toFixed(2)}`, `overall error: validated composite vs no-change baseline (RMSE ${sel.rmse} vs ${nc.rmse})`);
stat(s, 8.6, 3.65, 4.1, `${sel.lead} of 33`, `largest party correct; the baseline also scores ${nc.lead}/33, so this is an easy test`);
body(s, 8.6, 5.3, 4.1, 1.5, [{ text: "Selected: ", options: { bold: true } }, { text: "no change for ANC, DA, UDM, EFF, ATM; random forest for OTHER. The prototype's 2.50 and 32/33 were chosen on 2021 and are not valid." }], 13);
s.addNotes("[Presenter 3] For party support we model each party's swing. Validation chose 'no change' for the ANC, DA and UDM; the EFF and ATM did not exist in a validation fold, so they default to 'no change'; a random forest won for the OTHER category. On the locked 2021 test, the composite's error was 2.69 points against 2.93 for pure 'no change'. 'Last swing' would have helped the ANC but hurt the DA badly. All approaches identify the largest party in nearly every municipality, which tells us that leadership is easy to predict; the informative output is how close each contest is.");

// 15. Turnout scenarios ------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "2026 turnout: one modelled pattern, three assumptions", "Each municipality keeps its 2021 relative position; only the provincial level changes"); tag(s, "assumption");
s.addImage({ path: path.join(HERE, "maps3.png"), x: M, y: 1.8, w: W - 2 * M, h: (W - 2 * M) * 578 / 2345 });
const scen = [["Repeat of 2021", D.levels[0], D.votes[0]], ["Partial recovery", D.levels[1], D.votes[1]], ["Return to 2016", D.levels[2], D.votes[2]]];
scen.forEach((c, i) => {
  const x = M + i * 3.0;
  s.addText(`${c[1].toFixed(1)}%`, { x, y: 5.15, w: 2.8, h: 0.65, fontFace: HF, fontSize: 30, bold: true, color: i === 1 ? ALOE : TEAL, margin: 0, isTextBox: true });
  s.addText(`${c[0]}: about ${c[2]} m votes`, { x, y: 5.8, w: 2.8, h: 0.5, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true });
});
body(s, 9.6, 5.15, 3.1, 1.4, [{ text: `Municipal band ±${D.band} pts. `, options: { bold: true } }, { text: "Levels are assumptions, not forecasts. Votes use 2021 registration until the 2026 snapshot is added." }], 12);
s.addNotes("[Presenter 4] For 2026 we combine what the data validated with what it cannot tell us. The municipal pattern is modelled: each municipality keeps its 2021 position relative to the province, with a band of about 3.8 points from historical errors. The provincial level is an assumption, so we show three: a repeat of 2021 at 48 percent, partial recovery at 52, and a return to 2016 at 56. The maps differ only in overall shade. We do not claim any one of these is the forecast. Expected votes use 2021 registration until the 2026 IEC snapshot is added.");

// 16. Party scenarios -----------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "2026 party support: few contests are genuinely open", "Uniform swing from leader to runner-up needed to change the largest party (status-quo scenario)"); tag(s, "assumption");
s.addChart(pres.charts.BAR, [{ name: "Swing needed (pts)", labels: D.close.labels.map((l, i) => `${l} (${D.close.leader[i]} over ${D.close.runner[i]})`), values: D.close.swing }],
  { x: M, y: 1.85, w: 7.6, h: 4.8, barDir: "bar", ...axis, chartColors: [TEAL], showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelColor: INK, catAxisOrientation: "maxMin", valAxisMinVal: 0, catAxisLabelFontSize: 11 });
stat(s, 8.6, 2.0, 4.1, `ANC ${D.leaders.ANC}, DA ${D.leaders.DA}`, "municipalities by largest party under the validated status-quo scenario");
stat(s, 8.6, 3.65, 4.1, `${D.close.gap[0].toFixed(2)} pts`, `${D.close.labels[0]} lead: too close to call (threshold 2 x ${D.partymae} pts)`, ALOE);
body(s, 8.6, 5.3, 4.1, 1.5, [{ text: "Not modelled: ", options: { bold: true } }, { text: "parties formed after 2021, coalitions, candidates, the 2024 national election. The dashboard lets users test their own swings." }], 13);
s.addNotes("[Presenter 4] Under the validated status-quo scenario the ANC has the largest share in 31 municipalities and the DA in 2. But the more useful question is how close each contest is. Nelson Mandela Bay's lead is under half a point, far inside our typical error of 2.7 points, so we call it too close to call. Dr Beyers Naude would change hands with a uniform swing of about 3.6 points; most other municipalities would need ten points or more. We do not model new parties, coalitions or the 2024 national election, which is why the dashboard lets users explore swings themselves.");

// 17. Dashboard --------------------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "The dashboard: evidence and assumptions, clearly separated", "streamlit run app/app.py  |  ten pages from participation to limitations, with CSV downloads");
s.addImage({ path: path.join(HERE, "dashboard_overview.png"), x: M, y: 1.85, w: 5.95, h: 5.95 * 1425 / 2250 });
s.addImage({ path: path.join(HERE, "dashboard_scenarios.png"), x: 6.78, y: 1.85, w: 5.95, h: 5.95 * 1425 / 2250 });
s.addText("Overview: interactive map of any metric and election", { x: M, y: 5.68, w: 5.95, h: 0.35, fontFace: BF, fontSize: 12, color: GREY, margin: 0, isTextBox: true });
s.addText("Scenario explorer: choose the turnout level and party swings", { x: 6.78, y: 5.68, w: 5.95, h: 0.35, fontFace: BF, fontSize: 12, color: GREY, margin: 0, isTextBox: true });
body(s, M, 6.15, W - 2 * M, 0.8, [{ text: "Teal panels are validated evidence; orange panels are assumptions. ", options: { bold: true } }, { text: "The scenario explorer calls the same code as Notebook 06, and maps work offline." }], 14);
s.addNotes("[Presenter 4] The dashboard follows the story of this talk: participation, competition, socioeconomic context, historical validation, 2026 scenarios and limitations, plus a profile for each municipality and CSV downloads. One design rule runs throughout: teal panels show validated evidence, orange panels mark assumptions. The scenario explorer calls exactly the same code as our final notebook, so the dashboard cannot drift from the analysis. [Optional: switch to a live demo here.]");

// 18. Limitations ---------------------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "Limitations, and how we handled them");
const lim = [["Small sample", "Five elections, 33 municipalities", "Simple models, baselines, honest error bands"], ["Ecological data", "Associations describe places, not voters", "No causal or individual-level claims"],
  ["2021 shock", "COVID-era fall nobody could foresee", "Level treated as a scenario assumption"], ["Boundaries", "Merged units are comparable, not identical", "Explicit crosswalk, same for maps"],
  ["Census provenance", "Upstream tables of our census file unrecorded", "Flagged; no headline result depends on it"], ["Missing context", "No province-wide gender data; 2026 registration not yet extracted", "Pipeline ready to ingest it"]];
lim.forEach((l, i) => {
  const col = i % 2, row = Math.floor(i / 2), x = M + col * 6.15, y = 1.55 + row * 1.8;
  card(s, x, y, 5.95, 1.6, MIST);
  s.addText(l[0], { x: x + 0.25, y: y + 0.15, w: 5.5, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: TEAL, margin: 0, isTextBox: true });
  s.addText([{ text: l[1], options: { breakLine: true } }, { text: l[2], options: { color: GREY, italic: true } }], { x: x + 0.25, y: y + 0.6, w: 5.5, h: 0.9, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true, valign: "top" });
});
s.addNotes("[Presenter 4] We want to be clear about what this work cannot do. Five elections and 33 municipalities is a small sample. Our findings describe municipalities, not individual voters, and they are associations, not causes. The 2021 shock could not be anticipated, which is why the provincial level is an assumption. Merged municipalities are comparable but not identical over time. We could not verify the upstream tables of our census file, and there is no province-wide gender data; the 2026 registration snapshot is not yet extracted, but the pipeline is ready for it.");

// 19. Contribution -------------------------------------------------------------------------------------------------
s = pres.addSlide(); s.background = { color: INK };
s.addText("What we contribute", { x: M, y: 0.5, w: 8, h: 0.8, fontFace: HF, fontSize: 32, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
const contrib = [["A validated municipal panel", "Five elections on one geography, matching the IEC's official figures"], ["A clear finding", "Turnout's provincial level moves with events; its municipal pattern is stable"],
  ["An honest test", "Methods chosen before 2021 and tested once; simple persistence wins"], ["A usable tool", "Dashboard separating evidence from assumption, with open data downloads"]];
contrib.forEach((c, i) => {
  const y = 1.6 + i * 1.15;
  s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.05, w: 0.5, h: 0.5, fill: { color: TEAL }, line: { color: TEAL } });
  s.addText(String(i + 1), { x: M, y: y + 0.05, w: 0.5, h: 0.5, fontFace: BF, fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText([{ text: c[0], options: { bold: true, color: "FFFFFF", breakLine: true } }, { text: c[1], options: { color: "B8C4C2" } }], { x: M + 0.8, y, w: 6.6, h: 0.95, fontFace: BF, fontSize: 16, margin: 0, isTextBox: true, valign: "top" });
});
s.addText("Next steps", { x: 8.3, y: 1.6, w: 4.4, h: 0.5, fontFace: HF, fontSize: 22, bold: true, color: TEAL_L, margin: 0, isTextBox: true });
s.addText(bullets(["Add the IEC 2026 registration snapshot (age and gender)", "Train only on post-2011 transitions, when patterns stabilised", "Extend to ward level and other provinces", "Update after the 4 November 2026 results"]),
  { x: 8.3, y: 2.25, w: 4.4, h: 3.5, fontFace: BF, fontSize: 15, color: "FFFFFF", margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 10 });
s.addText("Thank you", { x: M, y: 6.5, w: 6, h: 0.6, fontFace: HF, fontSize: 24, bold: true, color: TEAL_L, margin: 0, isTextBox: true });
s.addNotes("[Presenter 4, then all] To close: we built a validated twenty-year municipal panel; we found that the provincial turnout level moves with events while each municipality's relative position is stable; we tested our models honestly with 2021 locked away; and we built a dashboard that separates evidence from assumption. Next we would add the 2026 registration data, try training only on the stable post-2011 period, and update everything after the November results. Thank you; we welcome your questions.");

// 20. References ------------------------------------------------------------------------------------------------------
s = pres.addSlide(); title(s, "References");
const refs = [
  "Electoral Commission of South Africa (IEC). Municipal election results downloads, LGE 2000-2021. results.elections.org.za/home/downloads/me-results",
  "IEC. Voter Turnout Reports, LGE 2000-2021. results.elections.org.za",
  "IEC. Voter Registration Statistics. elections.org.za/pw/StatsData/Voter-Registration-Statistics",
  "Statistics South Africa. Census 2011 and Census 2022. census.statssa.gov.za (upstream tables of our census file not recorded; see docs/DATA_SOURCES.md)",
  "Municipal Demarcation Board 2011 local municipal boundaries, via github.com/datawizzards/zadmaps",
  "Laakso, M. & Taagepera, R. (1979). 'Effective' number of parties. Comparative Political Studies, 12(1), 3-27.",
  "Geys, B. (2006). Explaining voter turnout: a review of aggregate-level research. Electoral Studies, 25(4), 637-663.",
  "Robinson, W.S. (1950). Ecological correlations and the behavior of individuals. American Sociological Review, 15(3), 351-357.",
  "Simpson, E.H. (1951). The interpretation of interaction in contingency tables. JRSS Series B, 13(2), 238-241.",
  "Hyndman, R.J. & Athanasopoulos, G. (2021). Forecasting: Principles and Practice (3rd ed.), section 5.10. otexts.com/fpp3",
  "Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. JMLR, 12, 2825-2830.",
  "Seabold, S. & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. Proc. 9th Python in Science Conf."];
s.addText(refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })), { x: M, y: 1.4, w: W - 2 * M, h: 5.4, fontFace: BF, fontSize: 13, color: INK, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 7 });
source(s, "Code, data, notebooks and documentation: github.com/MonwabisiThebe/UFH-DIRISA-TEAM-QUALIFICATION");
s.addNotes("Reference slide; not presented aloud. All web sources should be checked and access dates added before submission.");

pres.writeFile({ fileName: REPO + "/presentation/DIRISA_UFH_Presentation.pptx" }).then(f => console.log("wrote", f));
