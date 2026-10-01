"""Single source of truth for headline numbers, plus the verification report.

Reads ONLY the processed outputs written by notebooks 01-06, then writes:
  data/processed/verification/headline_metrics.csv   every headline number, its value and source file
  docs/VERIFICATION_REPORT.md                        human-readable acceptance report

It also scans the repository text for obsolete prototype metrics outside the places
where they are deliberately quoted as superseded.

Run:  python src/validation/headline_metrics.py   (run_pipeline.py calls it automatically)
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402

OUT = C.PROCESSED / "verification"

# Obsolete prototype numbers. They may appear ONLY where they are quoted as superseded.
STALE = {"7.725": "prototype turnout MAE (selected on 2021)", "2.502": "prototype party MAE (selected on 2021)",
         "Average Change Baseline": "prototype turnout method name"}
STALE_ALLOWED = {"docs/CHANGES_FROM_PROTOTYPE.md", "docs/VERIFICATION_REPORT.md",
                 "src/validation/headline_metrics.py", "notebooks/04_turnout_model.ipynb",
                 "notebooks/05_party_support_model.ipynb", "presentation/PRESENTATION_SCRIPT.md",
                 "docs/MODEL_VALIDATION.md",
                 "data/processed/models/phase5/party_backtest_summary.csv"}


def rd(phase, name):
    return pd.read_csv(C.DIRS[phase] / name)


def collect() -> pd.DataFrame:
    rows = []

    def add(section, metric, value, source, note=""):
        rows.append({"Section": section, "Metric": metric, "Value": value, "Source": source, "Note": note})

    # --- Data and validation -------------------------------------------------
    panel = rd("phase1", "municipality_election_panel_2000_2021.csv")
    src = "elections/phase1/municipality_election_panel_2000_2021.csv"
    add("Data", "Municipality-election observations", len(panel), src)
    for y, n in panel.groupby("Year")["MuniCode"].nunique().items():
        add("Data", f"Municipalities in {y}", int(n), src)
    iec = rd("phase1", "validation_iec_official_municipal.csv")
    s = "elections/phase1/validation_iec_official_municipal.csv"
    for y, g in iec.groupby("Year"):
        add("IEC validation", f"{y}: municipalities with registered voters equal to IEC", int((g["RegisteredVoters"] == g["RegisteredVoters_IEC"]).sum()), s)
        add("IEC validation", f"{y}: mean absolute turnout difference vs IEC (pts)", round(g["TurnoutDiff_pts"].abs().mean(), 2), s)
    prov = rd("phase1", "validation_iec_official_province.csv")
    for _, r in prov.iterrows():
        add("IEC validation", f"{int(r['Year'])}: provincial registered-voter gap vs IEC", int(r["Difference"]),
            "elections/phase1/validation_iec_official_province.csv", r["Explanation"])

    # --- Participation and competition --------------------------------------
    summ = rd("phase3", "provincial_summary_by_year.csv")
    s = "panels/phase3/provincial_summary_by_year.csv"
    for _, r in summ.iterrows():
        y = int(r["Year"])
        add("Participation", f"{y}: mean municipal turnout (%)", round(r["MeanTurnout"], 2), s)
        add("Participation", f"{y}: registered-voter-weighted turnout (%)", round(r["WeightedTurnout"], 2), s)
        add("Competition", f"{y}: mean parties contesting", round(r["MeanParties"], 2), s)
        add("Competition", f"{y}: mean effective number of parties", round(r["MeanENP"], 2), s)
    chg = rd("phase3", "municipality_turnout_change.csv")
    s = "panels/phase3/municipality_turnout_change.csv"
    add("Participation", "Municipalities with lower turnout in 2021 than 2016", int((chg["Change_2016_2021_pts"] < 0).sum()), s)
    add("Participation", "Smallest fall 2016-2021 (pts)", round(chg["Change_2016_2021_pts"].max(), 1), s)
    add("Participation", "Largest fall 2016-2021 (pts)", round(chg["Change_2016_2021_pts"].min(), 1), s)
    add("Participation", "Mean change 2016-2021 (pts)", round(chg["Change_2016_2021_pts"].mean(), 1), s)
    m21 = rd("phase3", "master_panel_2000_2021.csv").query("Year == 2021")
    lo, hi = m21.loc[m21["Turnout_%"].idxmin()], m21.loc[m21["Turnout_%"].idxmax()]
    add("Participation", "Lowest turnout 2021", f"{lo['Municipality']} {lo['Turnout_%']:.1f}%", "panels/phase3/master_panel_2000_2021.csv")
    add("Participation", "Highest turnout 2021", f"{hi['Municipality']} {hi['Turnout_%']:.1f}%", "panels/phase3/master_panel_2000_2021.csv")

    # --- Socioeconomic context ------------------------------------------------
    at = rd("phase3", "turnout_associations_2011_2021.csv")
    s = "panels/phase3/turnout_associations_2011_2021.csv"
    for _, r in at.iterrows():
        add("Associations", f"{r['Variable']}: within-election r [95% CI]",
            f"{r['WithinYear_r']:+.2f} [{r['WithinYear_lo']:+.2f}, {r['WithinYear_hi']:+.2f}]", s,
            f"pooled {r['Pooled_r']:+.2f}; by year {r['r_2011']:+.2f}/{r['r_2016']:+.2f}/{r['r_2021']:+.2f}")
    add("Associations", "Variables whose pooled sign differs from within-election sign",
        ", ".join(at.loc[at["SignFlip"], "Variable"]), s)
    r2 = rd("phase3", "turnout_regression_r2.csv")
    for _, r in r2.iterrows():
        add("Associations", f"R2: {r['Model']}", round(r["R2"], 3), "panels/phase3/turnout_regression_r2.csv")
    per = rd("phase3", "turnout_persistence.csv")
    for _, r in per.iterrows():
        add("Associations", f"Relative-turnout persistence r, {r['Transition']}", round(r["r_relative"], 2), "panels/phase3/turnout_persistence.csv")

    # --- Turnout model --------------------------------------------------------
    rel = rd("phase4", "turnout_relative_scores.csv")
    sel = rd("phase4", "turnout_model_selection.csv")
    full = rd("phase4", "turnout_full_scores.csv")
    s = "models/phase4/turnout_relative_scores.csv"
    best = sel.iloc[0]["Model"]
    add("Turnout model", "Selected relative model (validation folds 2011, 2016 only)", best, "models/phase4/turnout_model_selection.csv")
    for _, r in sel.iterrows():
        add("Turnout model", f"Mean validation MAE: {r['Model']}", round(r["MeanValidationMAE"], 2), "models/phase4/turnout_model_selection.csv")
    t = rel[(rel["TestYear"] == 2021) & (rel["Model"] == best)].iloc[0]
    add("Turnout model", "Locked 2021 test: relative-pattern MAE (pts)", round(t["MAE"], 2), s)
    add("Turnout model", "Locked 2021 test: relative-pattern r", round(t["r"], 2), s)
    f = full[(full["TestYear"] == 2021) & (full["RelativeModel"] == best) & (full["LevelMethod"] == "Previous level")].iloc[0]
    add("Turnout model", "Locked 2021 test: absolute turnout MAE (pts)", round(f["MAE"], 2), "models/phase4/turnout_full_scores.csv",
        "includes the province-wide 2021 fall")
    add("Turnout model", "Locked 2021 test: absolute mean error (pts, + = too high)", round(f["Bias"], 2), "models/phase4/turnout_full_scores.csv")
    add("Turnout model", "Provincial-average baseline, 2021 relative MAE (pts)",
        round(rel[(rel["TestYear"] == 2021) & rel["Model"].str.startswith("Provincial")]["MAE"].iloc[0], 2), s)
    cc = rd("phase4", "turnout_census_check.csv")
    for _, r in cc.iterrows():
        add("Turnout model", f"Census check (train 2016, test 2021): {r['Inputs']} MAE", round(r["MAE"], 2), "models/phase4/turnout_census_check.csv")
    band = rd("phase4", "turnout_error_band.csv").set_index("Quantity")["Value"]
    add("Turnout model", "Municipal error band, 80th percentile (pts)", band["80% of historical absolute errors below (pts)"], "models/phase4/turnout_error_band.csv")

    # --- Party model ----------------------------------------------------------
    meth = rd("phase5", "party_selected_methods.csv")
    add("Party model", "Selected methods", "; ".join(f"{a}: {b}" for a, b in zip(meth["Party"], meth["SelectedMethod"])),
        "models/phase5/party_selected_methods.csv")
    ps = rd("phase5", "party_backtest_summary.csv")
    s = "models/phase5/party_backtest_summary.csv"
    for _, r in ps.iterrows():
        pre = "Comparison only (selected on 2021, not a locked test)" if str(r["Approach"]).startswith("Prototype") else "Locked 2021"
        if pre != "Locked 2021":
            add("Party model", f"{pre}: prototype overall MAE", round(r["OverallMAE"], 2), s)
            add("Party model", f"{pre}: prototype largest party correct", f"{int(r['LeaderMatches'])}/{int(r['Municipalities'])}", s)
            continue
        add("Party model", f"Locked 2021: {r['Approach']}: overall MAE", round(r["OverallMAE"], 2), s)
        if pd.notna(r.get("OverallRMSE")):
            add("Party model", f"Locked 2021: {r['Approach']}: overall RMSE", round(r["OverallRMSE"], 2), s)
        add("Party model", f"Locked 2021: {r['Approach']}: largest party correct", f"{int(r['LeaderMatches'])}/{int(r['Municipalities'])}", s)

    # --- Scenarios ------------------------------------------------------------
    sc = rd("phase6", "municipality_scenarios_2026.csv")
    s = "scenarios/phase6/municipality_scenarios_2026.csv"
    for key, lab in [("Repeat2021", "repeat of 2021"), ("PartialRecovery", "partial recovery"), ("Return2016", "return to 2016")]:
        add("Scenarios", f"Assumed provincial level, {lab} (%)", round(sc[f"Turnout_{key}_%"].mean(), 2), s, "assumption, not a forecast")
        add("Scenarios", f"Expected votes cast, {lab}", int(sc[f"ExpectedVotes_{key}"].sum()), s, sc["RegistrationBasis"].iloc[0])
    vc = sc["Validated_Leader"].value_counts()
    for p_, n in vc.items():
        add("Scenarios", f"Validated status quo: municipalities with {p_} largest", int(n), s)
    tc = sc[sc["Validated_Status"] == "Too close to call"]
    add("Scenarios", "Validated status quo: too close to call", ", ".join(f"{r.Municipality} (gap {r.Validated_Gap_pts:.2f})" for r in tc.itertuples()), s)
    nxt = sc[sc["Validated_Status"] != "Too close to call"].nsmallest(1, "Validated_Gap_pts").iloc[0]
    add("Scenarios", "Next closest municipality: swing needed (pts)", f"{nxt['Municipality']} {nxt['SwingNeeded_pts']:.2f}", s)
    tcount = sc["Trend_Leader"].value_counts()
    add("Scenarios", "Trend-continues: largest-party counts", ", ".join(f"{a} {b}" for a, b in tcount.items()), s)
    return pd.DataFrame(rows)


def notebook_status() -> pd.DataFrame:
    rows = []
    for nb_path in sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb")):
        nb = nbformat.read(nb_path, as_version=4)
        code = [c for c in nb.cells if c.cell_type == "code"]
        executed = [c for c in code if c.get("execution_count")]
        errors = sum(1 for c in code for o in c.get("outputs", []) if o.get("output_type") == "error")
        order = [c["execution_count"] for c in executed]
        rows.append({"Notebook": nb_path.name, "CodeCells": len(code), "Executed": len(executed),
                     "InOrder": order == sorted(order) and order == list(range(1, len(order) + 1)), "Errors": errors})
    return pd.DataFrame(rows)


def stale_scan() -> list[str]:
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or "legacy_prototype" in p.parts or p.suffix not in {".py", ".md", ".ipynb", ".csv", ".toml", ".txt"}:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in STALE_ALLOWED or rel.startswith("data/raw"):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for k in STALE:
            if k in text:
                hits.append(f"{rel}: contains '{k}' ({STALE[k]})")
    return hits


def geography_check() -> tuple[int, bool]:
    g = json.loads(C.GEOJSON.read_text())
    ids = {f["id"] for f in g["features"]}
    return len(ids), ids == C.TARGET_CODES


def fallback_scan() -> list[str]:
    """Look for dummy/synthetic data generators in the app and src."""
    pats = re.compile(r"np\.random\.(rand|randn|normal|uniform|randint)|dummy|placeholder data|fake", re.I)
    hits = []
    for p in list((ROOT / "app").rglob("*.py")) + list((ROOT / "src").rglob("*.py")):
        if p.name == "headline_metrics.py":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if pats.search(line):
                hits.append(f"{p.relative_to(ROOT).as_posix()}:{i}: {line.strip()[:90]}")
    return hits


def write_report(metrics: pd.DataFrame, tests_summary: str | None = None) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT / "headline_metrics.csv", index=False)
    nbs = notebook_status()
    n_geo, geo_ok = geography_check()
    stale, fallback = stale_scan(), fallback_scan()

    def table(sec):
        d = metrics[metrics["Section"] == sec]
        lines = ["| Metric | Value | Source (data/processed/...) |", "|---|---|---|"]
        lines += [f"| {r.Metric} | {r.Value}{(' (' + r.Note + ')') if r.Note else ''} | `{r.Source}` |" for r in d.itertuples()]
        return "\n".join(lines)

    md = [f"# Verification report", "",
          f"Generated by `src/validation/headline_metrics.py` on {date.today().isoformat()} from the processed outputs. "
          "Every number in the README, docs, dashboard and slides should match `data/processed/verification/headline_metrics.csv`.", "",
          "## 1. Notebooks executed in order", "",
          "| Notebook | Code cells | Executed | Sequential order | Errors |", "|---|---|---|---|---|"]
    md += [f"| {r.Notebook} | {r.CodeCells} | {r.Executed} | {'yes' if r.InOrder else 'NO'} | {r.Errors} |" for r in nbs.itertuples()]
    md += ["", "## 2. Model-selection protocol", "",
           "Rolling origin: fold 2011 (train 2006), fold 2016 (train 2006, 2011) are validation folds; fold 2021 (train "
           "2006-2016) is the locked test. Methods are selected by lowest mean MAE on 2011 and 2016 only, frozen, then "
           "evaluated once on 2021, then refit on all transitions through 2021 for 2026. `tests/test_outputs.py` re-derives "
           "both selections from the saved validation scores.", "",
           "## 3. Locked-2021 turnout result and baselines", "", table("Turnout model"), "",
           "## 4. Locked-2021 party-support result and baselines", "", table("Party model"), "",
           "## 5. Reproduced EDA results", "", table("Participation"), "", table("Competition"), "", table("Associations"), "",
           "## 6. External validation against IEC official turnout reports", "", table("IEC validation"), "",
           "## 7. Scenario methodology and results", "",
           "Municipal turnout = assumed provincial level (scenario) + modelled relative position; party shares = validated "
           "methods refit through 2021 (status quo) or repeated 2016-2021 swing (trend continues, not validated). "
           "Registered voters: see note. These are scenarios, not forecasts.", "", table("Scenarios"), "",
           "## 8. Integrity checks", "",
           f"- Map geography: {n_geo} features; identical to the 33 analytical codes: **{'yes' if geo_ok else 'NO'}**",
           f"- Dummy or synthetic fallback data in `app/` or `src/`: **{'none found' if not fallback else '; '.join(fallback)}**",
           f"- Obsolete prototype metrics outside documented comparisons: **{'none found' if not stale else '; '.join(stale)}**",
           f"- Validator and tests: {tests_summary or 'see run_pipeline.py output'}", ""]
    path = ROOT / "docs" / "VERIFICATION_REPORT.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path


if __name__ == "__main__":
    summary = sys.argv[1] if len(sys.argv) > 1 else None
    p = write_report(collect(), summary)
    print("Wrote", p.relative_to(ROOT), "and data/processed/verification/headline_metrics.csv")
