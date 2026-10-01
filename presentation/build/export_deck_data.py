"""Export every number and image the slide deck uses, from the processed outputs.

Run from the repository root after run_pipeline.py:
    python presentation/build/export_deck_data.py
    node presentation/build/build_deck.js        (needs: npm install pptxgenjs)
Optional dashboard screenshots: python presentation/build/capture_screenshots.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402
from src.data.geography import load_geojson  # noqa: E402
from src.visualization.style import apply_style, choropleth  # noqa: E402

d = C.DIRS
J = {}
summ = pd.read_csv(d["phase3"] / "provincial_summary_by_year.csv")
J["years"] = [str(y) for y in summ.Year]
J["mean"] = summ.MeanTurnout.round(2).tolist(); J["wt"] = summ.WeightedTurnout.round(2).tolist()
J["parties"] = summ.MeanParties.round(2).tolist(); J["enp"] = summ.MeanENP.round(2).tolist()
J["minT"] = summ.MinTurnout.round(1).tolist(); J["maxT"] = summ.MaxTurnout.round(1).tolist()
prov = pd.read_csv(d["phase5"] / "provincial_pr_shares_by_year.csv")
J["prov"] = {p: prov[p].round(2).tolist() for p in C.PARTIES}
iec = pd.read_csv(d["phase1"] / "validation_iec_official_municipal.csv")
J["iec"] = {str(y): {"x": g["Turnout_%_IEC"].round(2).tolist(), "y": g["Turnout_%"].round(2).tolist(),
                     "mad": round(float(g.TurnoutDiff_pts.abs().mean()), 2)} for y, g in iec.groupby("Year")}
chg = pd.read_csv(d["phase3"] / "municipality_turnout_change.csv")["Change_2016_2021_pts"]
J["chg"] = {"n": int((chg < 0).sum()), "min": round(float(chg.max()), 1), "max": round(float(chg.min()), 1), "mean": round(float(chg.mean()), 1)}
at = pd.read_csv(d["phase3"] / "turnout_associations_2011_2021.csv")
lab = {"Med": "Median age", "Water": "Piped water", "Formal": "Formal dwellings", "O65": "Aged 65+", "Matric": "Matric",
       "Elec": "Electricity", "ENP": "Effective no. of parties", "NumberOfParties": "Parties contesting",
       "NoSch": "No schooling", "U15": "Under-15 share", "Margin_pts": "Victory margin"}
a = at[at.Variable.isin(lab)].sort_values("WithinYear_r")
J["assoc"] = {"labels": [lab[v] for v in a.Variable], "within": a.WithinYear_r.round(2).tolist(), "pooled": a.Pooled_r.round(2).tolist()}
J["r2"] = pd.read_csv(d["phase3"] / "turnout_regression_r2.csv").R2.round(2).tolist()
per = pd.read_csv(d["phase3"] / "turnout_persistence.csv")
J["persist"] = {"labels": per.Transition.tolist(), "r": per.r_relative.round(2).tolist()}
m = pd.read_csv(d["phase3"] / "master_panel_2000_2021.csv"); m21 = m[m.Year == 2021]
J["relscatter"] = {"x": m21.PreviousRelative_pts.round(2).tolist(), "y": m21.RelativeTurnout_pts.round(2).tolist()}
rel = pd.read_csv(d["phase4"] / "turnout_relative_scores.csv")
t = rel.pivot_table(index="Model", columns="TestYear", values="MAE"); t["mv"] = t[[2011, 2016]].mean(axis=1); t = t.sort_values("mv")
J["turn"] = {"labels": [i.replace(" (no municipal pattern)", "") for i in t.index], "val": t.mv.round(2).tolist(), "test": t[2021].round(2).tolist()}
full = pd.read_csv(d["phase4"] / "turnout_full_scores.csv")
f = full[(full.TestYear == 2021) & (full.RelativeModel == "Relative persistence") & (full.LevelMethod == "Previous level")].iloc[0]
r = rel[(rel.TestYear == 2021) & (rel.Model == "Relative persistence")].iloc[0]
J["abs"] = {"mae": round(float(f.MAE), 2), "bias": round(float(f.Bias), 2)}
J["relt"] = {"mae": round(float(r.MAE), 2), "r": round(float(r.r), 2)}
band = pd.read_csv(d["phase4"] / "turnout_error_band.csv").set_index("Quantity").Value
J["band"] = round(float(band["80% of historical absolute errors below (pts)"]), 2)
ps = pd.read_csv(d["phase5"] / "party_backtest_summary.csv")
J["party"] = {row.Approach: {"mae": round(float(row.OverallMAE), 2),
                             "rmse": None if pd.isna(row.OverallRMSE) else round(float(row.OverallRMSE), 2),
                             "lead": int(row.LeaderMatches),
                             "per": [None if pd.isna(row.get(f"MAE_{p}")) else round(float(row[f"MAE_{p}"]), 2) for p in C.PARTIES]}
              for _, row in ps.iterrows()}
J["partymae"] = round(float(ps.iloc[0].OverallMAE), 2)
sc = pd.read_csv(d["phase6"] / "municipality_scenarios_2026.csv")
keys = ["Repeat2021", "PartialRecovery", "Return2016"]
J["levels"] = [round(float(sc[f"Turnout_{k}_%"].mean()), 1) for k in keys]
J["votes"] = [round(float(sc[f"ExpectedVotes_{k}"].sum()) / 1e6, 2) for k in keys]
J["leaders"] = {k: int(v) for k, v in sc.Validated_Leader.value_counts().items()}
cl = sc.nsmallest(7, "Validated_Gap_pts")
J["close"] = {"labels": cl.Municipality.tolist(), "swing": cl.SwingNeeded_pts.round(2).tolist(), "gap": cl.Validated_Gap_pts.round(2).tolist(),
              "leader": cl.Validated_Leader.tolist(), "runner": cl.Validated_RunnerUp.tolist()}
pn = pd.read_csv(d["phase1"] / "municipality_election_panel_2000_2021.csv")
J["nobs"] = len(pn); J["vd"] = int(pn[pn.Year == 2021].VotingDistricts.sum())
(HERE / "deck_data.json").write_text(json.dumps(J, indent=1))

# Images: title map, five-election maps, three scenario maps
apply_style(); geo = load_geojson()
cm = LinearSegmentedColormap.from_list("t", ["#2E6F69", "#7FB5AE", "#E8F2EF"])
fig, ax = plt.subplots(figsize=(8, 5.2)); fig.patch.set_alpha(0)
choropleth(ax, geo, dict(zip(m21.MuniCode, m21["Turnout_%"])), cmap=cm, vmin=38, vmax=60, edge="#1E2B2F"); ax.set_axis_off()
fig.savefig(HERE / "title_map.png", dpi=200, transparent=True, bbox_inches="tight", pad_inches=0)
fig, axes = plt.subplots(1, 5, figsize=(16, 3.3))
for ax, y in zip(axes, C.ELECTION_YEARS):
    dd = m[m.Year == y]; sm = choropleth(ax, geo, dict(zip(dd.MuniCode, dd["Turnout_%"])), vmin=38, vmax=70)
    ax.set_title(str(y), fontsize=15, fontweight="bold"); ax.set_axis_off()
cb = fig.colorbar(sm, ax=axes, orientation="horizontal", shrink=.3, pad=.03, aspect=40)
cb.set_label("Turnout (%)  (grey = no data: Matatiele was in KwaZulu-Natal in 2000)", fontsize=11); cb.outline.set_visible(False)
fig.savefig(HERE / "maps5.png", dpi=200, bbox_inches="tight", pad_inches=0.05)
fig, axes = plt.subplots(1, 3, figsize=(15, 3.9))
for ax, (k, lab_) in zip(axes, [("Repeat2021", "Repeat of 2021"), ("PartialRecovery", "Partial recovery"), ("Return2016", "Return to 2016")]):
    sm = choropleth(ax, geo, dict(zip(sc.MuniCode, sc[f"Turnout_{k}_%"])), vmin=38, vmax=66)
    ax.set_title(lab_, fontsize=15, fontweight="bold"); ax.set_axis_off()
cb = fig.colorbar(sm, ax=axes, orientation="horizontal", shrink=.3, pad=.03, aspect=40)
cb.set_label("Scenario turnout (%)", fontsize=11); cb.outline.set_visible(False)
fig.savefig(HERE / "maps3.png", dpi=200, bbox_inches="tight", pad_inches=0.05)
print("Wrote deck_data.json and map images to", HERE.relative_to(ROOT))
