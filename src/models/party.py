"""PR party-support models with rolling-origin validation.

Each party category (ANC, DA, EFF, UDM, ATM, OTHER) is modelled as a vote-share
SWING from the previous election, then the six predictions are clipped at zero
and renormalised so each municipality's composition sums to 100%.

Same time-ordered folds as the turnout model:
    fold 2011 (train: 2006 transition)              -> validation
    fold 2016 (train: 2006, 2011 transitions)       -> validation
    fold 2021 (train: 2006, 2011, 2016 transitions) -> final test

Selection rule (pre-declared): per party, lowest mean MAE over the validation
folds in which the party already existed in the previous election. A party with
no such fold (EFF first contested in 2016, ATM in 2021) cannot be validated, so it
defaults to "No change" -- the simplest, assumption-free method.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import PARTIES
from src.models.evaluation import metrics
from src.models.turnout import FOLDS, TEST_FOLD

CONTEXT = ["PreviousTurnout_%", "PreviousENP", "PreviousMargin_pts", "LogPreviousRegistered"]
DEFAULT_METHOD = "No change"


def _features(p):
    return [f"Prev_{p}"] + CONTEXT


def party_models():
    """name -> fn(train, test, party) -> predicted share (before composition)."""
    def no_change(tr, te, p):
        return te[f"Prev_{p}"].to_numpy()

    def average_swing(tr, te, p):
        return te[f"Prev_{p}"].to_numpy() + tr[f"Swing_{p}"].mean()

    def last_swing(tr, te, p):
        last = tr["Year"].max()
        return te[f"Prev_{p}"].to_numpy() + tr.loc[tr["Year"] == last, f"Swing_{p}"].mean()

    def ridge(tr, te, p):
        m = make_pipeline(StandardScaler(), RidgeCV(alphas=[0.1, 1, 3, 10, 30, 100]))
        return te[f"Prev_{p}"].to_numpy() + m.fit(tr[_features(p)], tr[f"Swing_{p}"]).predict(te[_features(p)])

    def forest(tr, te, p):
        m = RandomForestRegressor(n_estimators=500, max_depth=3, min_samples_leaf=4, random_state=42)
        return te[f"Prev_{p}"].to_numpy() + m.fit(tr[_features(p)], tr[f"Swing_{p}"]).predict(te[_features(p)])

    return {"No change": no_change, "Average swing": average_swing, "Last swing": last_swing,
            "Ridge regression": ridge, "Random forest": forest}


def modelling_frame(master: pd.DataFrame) -> pd.DataFrame:
    return master.dropna(subset=[f"Prev_{p}" for p in PARTIES] + CONTEXT).copy()


def compose(matrix: np.ndarray) -> np.ndarray:
    """Clip negatives and renormalise rows to 100%."""
    m = np.clip(np.asarray(matrix, dtype=float), 0, None)
    s = m.sum(axis=1, keepdims=True)
    s[s == 0] = 1.0
    return 100 * m / s


def rolling_origin(master: pd.DataFrame):
    """Per-party scores for every model and fold, plus raw predictions."""
    df = modelling_frame(master)
    rows, preds = [], {}
    for test_year, train_years in FOLDS.items():
        tr = df[df["Year"].isin(train_years)]
        te = df[df["Year"] == test_year].sort_values("MuniCode")
        role = "test" if test_year == TEST_FOLD else "validation"
        for p in PARTIES:
            existed = bool((te[f"Prev_{p}"] > 0).any())
            trainable = bool((tr[f"Prev_{p}"] > 0).any())
            for name, fn in party_models().items():
                if name in ("Ridge regression", "Random forest") and not trainable:
                    continue  # cannot learn a swing model for a party absent from training
                pred = fn(tr, te, p)
                preds[(test_year, p, name)] = pred
                rows.append({"TestYear": test_year, "Role": role, "Party": p, "Model": name,
                             "PartyExistedBefore": existed,
                             **metrics(te[p], np.clip(pred, 0, None))})
    return pd.DataFrame(rows), preds


def select_methods(scores: pd.DataFrame) -> pd.DataFrame:
    """Apply the pre-declared selection rule; never looks at the test fold."""
    out = []
    for p in PARTIES:
        v = scores[(scores["Party"] == p) & (scores["Role"] == "validation") & scores["PartyExistedBefore"]]
        if v.empty:
            out.append({"Party": p, "SelectedMethod": DEFAULT_METHOD, "MeanValidationMAE": np.nan,
                        "ValidationFolds": 0,
                        "Reason": "No validation fold: party absent from the previous election; default rule"})
            continue
        agg = v.groupby("Model")["MAE"].agg(["mean", "count"])
        agg = agg[agg["count"] == agg["count"].max()].sort_values("mean")
        out.append({"Party": p, "SelectedMethod": agg.index[0], "MeanValidationMAE": float(agg["mean"].iloc[0]),
                    "ValidationFolds": int(agg["count"].iloc[0]),
                    "Reason": "Lowest mean validation MAE (2011 and 2016 folds)"})
    return pd.DataFrame(out)


def composite_test(master: pd.DataFrame, preds: dict, methods: dict, test_year: int = TEST_FOLD):
    """Build a 100%-composition prediction for one fold from per-party methods."""
    te = modelling_frame(master)
    te = te[te["Year"] == test_year].sort_values("MuniCode")
    mat = compose(np.column_stack([preds[(test_year, p, methods[p])] for p in PARTIES]))
    actual = te[PARTIES].to_numpy()
    out = te[["MuniCode", "Year"]].copy()
    for i, p in enumerate(PARTIES):
        out[f"Actual_{p}"] = actual[:, i]
        out[f"Pred_{p}"] = mat[:, i]
    out["ActualLeader"] = [PARTIES[i] for i in actual.argmax(1)]
    out["PredLeader"] = [PARTIES[i] for i in mat.argmax(1)]
    srt = np.sort(actual, axis=1)
    out["ActualLeadGap_pts"] = srt[:, -1] - srt[:, -2]
    summary = {
        "OverallMAE": float(np.abs(actual - mat).mean()),
        "OverallRMSE": float(np.sqrt(((actual - mat) ** 2).mean())),
        "LeaderMatches": int((out["ActualLeader"] == out["PredLeader"]).sum()),
        "Municipalities": int(len(out)),
        **{f"MAE_{p}": float(np.abs(actual[:, i] - mat[:, i]).mean()) for i, p in enumerate(PARTIES)},
    }
    return out.reset_index(drop=True), summary
