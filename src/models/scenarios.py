"""2026 scenario engine, shared by Notebook 06 and the Streamlit dashboard.

A 2026 scenario has two clearly separated parts:

1. **Validated municipal pattern** (from historical backtests): each
   municipality's relative turnout position and its party composition under
   the selected methods.
2. **Stated assumptions** (not predictable from five elections): the provincial
   turnout level and any uniform party swing. These are scenario levers, shown
   to users as assumptions rather than findings.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import PARTIES
from src.models import party as party_models_mod
from src.models import turnout as turnout_models_mod
from src.models.party import compose


# ----------------------------------------------------------------------------
# Feature state for 2026 (latest observed election = 2021)
# ----------------------------------------------------------------------------
def state_2026(master: pd.DataFrame) -> pd.DataFrame:
    """Re-label 2021 outcomes as the 'previous election' inputs for 2026."""
    s = master[master["Year"] == 2021].copy().sort_values("MuniCode")
    st = pd.DataFrame({
        "MuniCode": s["MuniCode"].to_numpy(), "Year": 2026,
        "PreviousRelative_pts": s["RelativeTurnout_pts"].to_numpy(),
        "PreviousTurnout_%": s["Turnout_%"].to_numpy(),
        "PreviousENP": s["ENP"].to_numpy(),
        "PreviousMargin_pts": s["Margin_pts"].to_numpy(),
        "PreviousRegisteredVoters": s["RegisteredVoters"].to_numpy(),
        "LogPreviousRegistered": np.log(s["RegisteredVoters"].to_numpy()),
    })
    for p in PARTIES:
        st[f"Prev_{p}"] = s[p].to_numpy()
    return st.reset_index(drop=True)


def project_relative_turnout(master: pd.DataFrame, model_name: str) -> pd.DataFrame:
    """Refit the selected relative-turnout model on all targets 2006-2021."""
    train = turnout_models_mod.modelling_frame(master)
    st = state_2026(master)
    fn = turnout_models_mod.relative_models()[model_name]
    st["RelativeTurnout_2026"] = fn(train, st)
    return st


def project_party_shares(master: pd.DataFrame, methods: dict) -> pd.DataFrame:
    """Refit each party's selected method on all transitions and compose to 100%."""
    train = party_models_mod.modelling_frame(master)
    st = state_2026(master)
    fns = party_models_mod.party_models()
    raw = np.column_stack([fns[methods[p]](train, st, p) for p in PARTIES])
    shares = compose(raw)
    out = st[["MuniCode"]].copy()
    for i, p in enumerate(PARTIES):
        out[p] = shares[:, i]
    return out


def last_swing_shares(master: pd.DataFrame) -> pd.DataFrame:
    """Alternative 'trend continues' composition: repeat each party's mean
    2016->2021 swing. Plausible, but NOT selected by validation."""
    st = state_2026(master)
    sw = master[master["Year"] == 2021][[f"Swing_{p}" for p in PARTIES]].mean()
    raw = np.column_stack([st[f"Prev_{p}"] + sw[f"Swing_{p}"] for p in PARTIES])
    shares = compose(raw)
    out = st[["MuniCode"]].copy()
    for i, p in enumerate(PARTIES):
        out[p] = shares[:, i]
    return out


# ----------------------------------------------------------------------------
# Scenario levers
# ----------------------------------------------------------------------------
def turnout_level_presets(master: pd.DataFrame) -> dict:
    lv = master.groupby("Year")["ProvincialLevel_%"].first()
    return {
        "Repeat of 2021 conditions": float(lv[2021]),
        "Partial recovery (half the 2021 drop regained)": float(lv[2021] + 0.5 * (lv[2016] - lv[2021])),
        "Return to 2016 participation": float(lv[2016]),
    }


def turnout_scenario(relative: pd.DataFrame, level: float, band: float,
                     registered: pd.Series | None = None) -> pd.DataFrame:
    """Municipal turnout = provincial level assumption + modelled relative position.

    ``band`` is the empirical relative-error scale from the backtest; it does NOT
    include uncertainty about the provincial level, which is the scenario lever.
    """
    out = relative[["MuniCode", "RelativeTurnout_2026"]].copy()
    out["AssumedLevel_%"] = level
    out["Turnout_%"] = np.clip(level + out["RelativeTurnout_2026"], 0, 100)
    out["Low_%"] = np.clip(out["Turnout_%"] - band, 0, 100)
    out["High_%"] = np.clip(out["Turnout_%"] + band, 0, 100)
    if registered is not None:
        reg = out["MuniCode"].map(registered)
        out["RegisteredVoters"] = reg
        out["ExpectedVotesCast"] = (out["Turnout_%"] / 100 * reg).round()
    return out


def apply_swing(shares: pd.DataFrame, swings: dict | None = None) -> pd.DataFrame:
    """Add uniform percentage-point swings per party, then re-compose to 100%."""
    swings = swings or {}
    raw = np.column_stack([shares[p].to_numpy() + swings.get(p, 0.0) for p in PARTIES])
    comp = compose(raw)
    out = shares[["MuniCode"]].copy()
    for i, p in enumerate(PARTIES):
        out[p] = comp[:, i]
    return out


def leaders(shares: pd.DataFrame, close_threshold: float) -> pd.DataFrame:
    """Largest and second-largest category, gap, and a too-close-to-call flag.

    ``close_threshold`` should reflect historical error (e.g. 2 x party MAE):
    a gap smaller than that is not distinguishable from model error.
    """
    mat = shares[PARTIES].to_numpy()
    order = np.argsort(-mat, axis=1)
    out = shares[["MuniCode"]].copy()
    out["Leader"] = [PARTIES[i] for i in order[:, 0]]
    out["RunnerUp"] = [PARTIES[i] for i in order[:, 1]]
    out["LeaderShare_%"] = mat[np.arange(len(mat)), order[:, 0]]
    out["Gap_pts"] = out["LeaderShare_%"] - mat[np.arange(len(mat)), order[:, 1]]
    out["TooCloseToCall"] = out["Gap_pts"] < close_threshold
    out["Status"] = np.where(out["TooCloseToCall"], "Too close to call", "Clear lead under scenario")
    return out
