"""Contract tests on the processed outputs (run after the notebooks)."""
import json

import numpy as np
import pandas as pd
import pytest

from src import config as C

panel_path = C.DIRS["phase1"] / "municipality_election_panel_2000_2021.csv"
pytestmark = pytest.mark.skipif(not panel_path.exists(), reason="run the notebooks first")


def test_panel_shape_and_keys():
    p = pd.read_csv(panel_path)
    assert len(p) == 164
    assert p.groupby("Year")["MuniCode"].nunique().to_dict() == {2000: 32, 2006: 33, 2011: 33, 2016: 33, 2021: 33}
    assert set(p["MuniCode"]) == C.TARGET_CODES


def test_matches_iec_official_registration():
    v = pd.read_csv(C.DIRS["phase1"] / "validation_iec_official_municipal.csv")
    assert (v["RegisteredVoters"] == v["RegisteredVoters_IEC"]).all()
    assert v["TurnoutDiff_pts"].abs().mean() < 0.5


def test_no_future_census_in_backtests():
    k = pd.read_csv(C.DIRS["phase2"] / "demographics_as_known_2000_2026.csv")
    assert k.loc[k["Year"] <= 2011].filter(like="K_").isna().all().all()
    assert set(k.loc[k["Year"].isin([2016, 2021]), "CensusUsed"].astype(str)) == {"2011"}


def test_turnout_selection_ignores_test_fold():
    rel = pd.read_csv(C.DIRS["phase4"] / "turnout_relative_scores.csv")
    sel = pd.read_csv(C.DIRS["phase4"] / "turnout_model_selection.csv")
    best = rel[rel["Role"] == "validation"].groupby("Model")["MAE"].mean().idxmin()
    assert sel.iloc[0]["Model"] == best


def test_party_selection_ignores_test_fold():
    s = pd.read_csv(C.DIRS["phase5"] / "party_scores.csv")
    m = pd.read_csv(C.DIRS["phase5"] / "party_selected_methods.csv")
    for _, r in m.iterrows():
        v = s[(s["Party"] == r["Party"]) & (s["Role"] == "validation") & s["PartyExistedBefore"]]
        if v.empty:
            assert r["SelectedMethod"] == "No change"
        else:
            assert r["SelectedMethod"] == v.groupby("Model")["MAE"].mean().idxmin()


def test_scenarios_are_coherent():
    s = pd.read_csv(C.DIRS["phase6"] / "municipality_scenarios_2026.csv")
    assert s["MuniCode"].nunique() == 33
    for kind in ["Validated", "Trend"]:
        cols = [f"{p}_{kind}_%" for p in C.PARTIES]
        assert np.allclose(s[cols].sum(axis=1), 100)
    assert np.allclose(s["Turnout_Repeat2021_%"], s["Turnout_2021_%"])


def test_geojson_matches_geography():
    g = json.loads(C.GEOJSON.read_text())
    assert {f["id"] for f in g["features"]} == C.TARGET_CODES
