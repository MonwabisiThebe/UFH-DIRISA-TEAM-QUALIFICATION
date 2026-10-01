"""Master municipality x election panel and engineered features.

Key engineered features
-----------------------
Turnout_%            votes cast / registered voters (PR ballot)
ENP                  effective number of parties, 1 / sum(p_i^2), full distribution
Margin_pts           first-placed minus second-placed PR share
ProvincialLevel_%    unweighted mean municipal turnout in that election
RelativeTurnout_pts  Turnout_% - ProvincialLevel_%  (where a municipality sits
                     relative to the province; the quantity that turns out to be
                     persistent and predictable)
PreviousRelative_pts lag of the above
Lags                 previous turnout / ENP / margin / registered voters / shares
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import DISTRICTS, MUNICIPALITY_NAMES, PARTIES


def add_turnout_decomposition(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["ProvincialLevel_%"] = p.groupby("Year")["Turnout_%"].transform("mean")
    p["RelativeTurnout_pts"] = p["Turnout_%"] - p["ProvincialLevel_%"]
    p = p.sort_values(["MuniCode", "Year"])
    g = p.groupby("MuniCode")
    p["PreviousRelative_pts"] = g["RelativeTurnout_pts"].shift(1)
    p["PreviousProvincialLevel_%"] = g["ProvincialLevel_%"].shift(1)
    p["LogPreviousRegistered"] = np.log(p["PreviousRegisteredVoters"])
    return p.reset_index(drop=True)


def add_party_lags(party_wide: pd.DataFrame) -> pd.DataFrame:
    w = party_wide.sort_values(["MuniCode", "Year"]).copy()
    g = w.groupby("MuniCode")
    for p in PARTIES:
        w[f"Prev_{p}"] = g[p].shift(1)
        w[f"Swing_{p}"] = w[p] - w[f"Prev_{p}"]
    return w.reset_index(drop=True)


def build_master_panel(elections: pd.DataFrame, party_wide: pd.DataFrame,
                       demo_descriptive: pd.DataFrame, demo_known: pd.DataFrame) -> pd.DataFrame:
    """One row per municipality x election with every engineered feature."""
    m = add_turnout_decomposition(elections)
    m = m.merge(add_party_lags(party_wide), on=["MuniCode", "Year"], how="left", validate="one_to_one")
    m = m.merge(demo_descriptive, on=["MuniCode", "Year"], how="left", validate="one_to_one")
    m = m.merge(demo_known, on=["MuniCode", "Year"], how="left", validate="one_to_one")
    m["Municipality"] = m["MuniCode"].map(MUNICIPALITY_NAMES)
    m["District"] = m["MuniCode"].map(DISTRICTS)
    m["IsMetro"] = m["MuniCode"].isin(["BUF", "NMA"])
    return m.sort_values(["Year", "MuniCode"]).reset_index(drop=True)


def provincial_summary(master: pd.DataFrame) -> pd.DataFrame:
    """Per-election summary: unweighted mean, registered-weighted turnout, spread."""
    g = master.groupby("Year")
    s = g["Turnout_%"].agg(Municipalities="count", MeanTurnout="mean", MedianTurnout="median",
                           SDTurnout="std", MinTurnout="min", MaxTurnout="max")
    tot = g[["VotesCast", "RegisteredVoters", "ValidVotes"]].sum()
    s["WeightedTurnout"] = 100 * tot["VotesCast"] / tot["RegisteredVoters"]
    s["RegisteredVoters"] = tot["RegisteredVoters"]
    s["VotesCast"] = tot["VotesCast"]
    s["MeanENP"] = g["ENP"].mean()
    s["MeanParties"] = g["NumberOfParties"].mean()
    s["MeanMargin"] = g["Margin_pts"].mean()
    return s.reset_index().round(4)
