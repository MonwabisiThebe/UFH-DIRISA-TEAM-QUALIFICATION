"""End-to-end checks on the processed outputs that the dashboard and slides rely on.

Run after the notebooks:  python src/validation/validate_submission.py
Exits with a non-zero status if any check fails.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import config as C  # noqa: E402

REQUIRED = {
    "panel": C.DIRS["phase1"] / "municipality_election_panel_2000_2021.csv",
    "party_wide": C.DIRS["phase1"] / "party_shares_selected_wide_2000_2021.csv",
    "iec_muni": C.DIRS["phase1"] / "validation_iec_official_municipal.csv",
    "census": C.DIRS["phase2"] / "municipality_census_snapshots_2011_2022.csv",
    "as_known": C.DIRS["phase2"] / "demographics_as_known_2000_2026.csv",
    "master": C.DIRS["phase3"] / "master_panel_2000_2021.csv",
    "assoc": C.DIRS["phase3"] / "turnout_associations_2011_2021.csv",
    "turnout_rel": C.DIRS["phase4"] / "turnout_relative_scores.csv",
    "turnout_sel": C.DIRS["phase4"] / "turnout_model_selection.csv",
    "party_scores": C.DIRS["phase5"] / "party_scores.csv",
    "party_summary": C.DIRS["phase5"] / "party_backtest_summary.csv",
    "scen": C.DIRS["phase6"] / "municipality_scenarios_2026.csv",
    "geo": C.GEOJSON,
}


def run() -> list[str]:
    fails: list[str] = []

    def check(name, ok):
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            fails.append(name)

    missing = [str(p.relative_to(ROOT)) for p in REQUIRED.values() if not p.exists()]
    check("all required outputs exist" + (f" (missing: {missing})" if missing else ""), not missing)
    if missing:
        return fails

    d = {k: (pd.read_csv(v) if v.suffix == ".csv" else None) for k, v in REQUIRED.items()}
    panel, master, scen = d["panel"], d["master"], d["scen"]

    check("panel has 164 municipality-elections", len(panel) == 164)
    check("panel years are 2000-2021 LGEs", set(panel["Year"]) == set(C.ELECTION_YEARS))
    check("no duplicate municipality-years", not panel.duplicated(["MuniCode", "Year"]).any())
    check("turnout within 0-100", panel["Turnout_%"].between(0, 100).all())
    check("ENP >= 1", (panel["ENP"] >= 1).all())
    check("party categories sum to 100", np.allclose(d["party_wide"][C.PARTIES].sum(axis=1), 100))
    check("registered voters equal IEC official reports (2016, 2021)",
          (d["iec_muni"]["RegisteredVoters"] == d["iec_muni"]["RegisteredVoters_IEC"]).all())
    k = d["as_known"]
    check("no census information in as-known features for elections <= 2011",
          k.loc[k["Year"] <= 2011, [c for c in k if c.startswith("K_")]].isna().all().all())
    check("as-known features for 2021 come from Census 2011", (k.loc[k["Year"] == 2021, "CensusUsed"].astype(str) == "2011").all())

    rel = d["turnout_rel"]
    check("turnout model selected on validation folds only",
          set(rel.loc[rel["Role"] == "validation", "TestYear"]) == {2011, 2016})
    ps = d["party_scores"]
    check("party models validated on 2011/2016 and tested on 2021",
          set(ps.loc[ps["Role"] == "validation", "TestYear"]) == {2011, 2016}
          and set(ps.loc[ps["Role"] == "test", "TestYear"]) == {2021})

    check("33 municipalities in scenarios", scen["MuniCode"].nunique() == 33)
    for key in ["Repeat2021", "PartialRecovery", "Return2016"]:
        check(f"scenario turnout {key} within 0-100", scen[f"Turnout_{key}_%"].between(0, 100).all())
    for s in ["Validated", "Trend"]:
        cols = [f"{p}_{s}_%" for p in C.PARTIES]
        check(f"{s} party shares sum to 100 and are non-negative",
              np.allclose(scen[cols].sum(axis=1), 100) and (scen[cols] >= 0).all().all())
    check("map geography equals the 33 analytical codes",
          {f["id"] for f in __import__("json").loads(C.GEOJSON.read_text())["features"]} == C.TARGET_CODES)
    return fails


if __name__ == "__main__":
    failures = run()
    print("\nSubmission validation " + ("PASSED" if not failures else f"FAILED ({len(failures)} checks)"))
    sys.exit(1 if failures else 0)
