"""Municipal turnout models with rolling-origin (time-ordered) validation.

Decomposition
-------------
    Turnout[m, t] = Level[t] + Relative[m, t]

``Level`` is the provincial (unweighted mean municipal) turnout in election t.
``Relative`` is how far municipality m sits above/below that level.

The two components are treated differently because they behave differently:

* Relative position is highly persistent between elections and can be
  predicted from municipal history -> it is MODELLED and validated.
* The provincial level moves with province/nation-wide conditions (the 2021
  election fell ~8 points everywhere, during COVID-19). Five elections cannot
  validate a model of that -> it is a stated SCENARIO assumption in 2026.

Validation design (no random splits, no peeking at 2021)
--------------------------------------------------------
    fold 2011: train on 2006 targets              -> validation
    fold 2016: train on 2006, 2011 targets        -> validation
    fold 2021: train on 2006, 2011, 2016 targets  -> final test (reported once)

The method used in 2026 is chosen by mean validation MAE (2011 and 2016 folds)
BEFORE the 2021 test is inspected.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.models.evaluation import metrics

FOLDS = {2011: [2006], 2016: [2006, 2011], 2021: [2006, 2011, 2016]}
VALIDATION_FOLDS = [2011, 2016]
TEST_FOLD = 2021

TARGET = "RelativeTurnout_pts"
FEATURES = ["PreviousRelative_pts", "PreviousENP", "PreviousMargin_pts", "LogPreviousRegistered"]
KNOWN_DEMOGRAPHICS = ["K_U15", "K_Water", "K_Matric"]
RIDGE_ALPHAS = [0.1, 1, 3, 10, 30, 100]


def _ridge():
    return make_pipeline(StandardScaler(), RidgeCV(alphas=RIDGE_ALPHAS))


def _forest():
    return RandomForestRegressor(n_estimators=500, max_depth=3, min_samples_leaf=4, random_state=42)


def relative_models():
    """Candidate models for the relative-position component.

    Each entry maps a name to ``fit_predict(train, test) -> np.ndarray``.
    """
    def zero(tr, te):
        return np.zeros(len(te))

    def persistence(tr, te):
        return te["PreviousRelative_pts"].to_numpy()

    def shrunk(tr, te):
        x, y = tr["PreviousRelative_pts"], tr[TARGET]
        beta = float((x * y).sum() / (x ** 2).sum())
        return beta * te["PreviousRelative_pts"].to_numpy()

    def ridge(tr, te):
        return _ridge().fit(tr[FEATURES], tr[TARGET]).predict(te[FEATURES])

    def forest(tr, te):
        return _forest().fit(tr[FEATURES], tr[TARGET]).predict(te[FEATURES])

    return {
        "Provincial average (no municipal pattern)": zero,
        "Relative persistence": persistence,
        "Shrunk persistence": shrunk,
        "Ridge regression": ridge,
        "Random forest": forest,
    }


def level_methods():
    """Ways of setting the provincial level, used to rebuild full turnout."""
    def previous(levels, train_years, test_year):
        return levels[_prev_year(test_year)]

    def average_change(levels, train_years, test_year):
        changes = [levels[y] - levels[_prev_year(y)] for y in train_years]
        return levels[_prev_year(test_year)] + float(np.mean(changes))

    return {"Previous level": previous, "Average level change": average_change}


def _prev_year(y):
    return {2006: 2000, 2011: 2006, 2016: 2011, 2021: 2016, 2026: 2021}[y]


def modelling_frame(master: pd.DataFrame) -> pd.DataFrame:
    """Rows with a previous election (targets 2006-2021)."""
    return master.dropna(subset=["PreviousRelative_pts", "PreviousENP", "PreviousMargin_pts",
                                 "LogPreviousRegistered"]).copy()


def rolling_origin(master: pd.DataFrame):
    """Evaluate every relative model and every level x relative combination.

    Returns ``(relative_scores, full_scores, predictions)``.
    """
    df = modelling_frame(master)
    levels = master.groupby("Year")["ProvincialLevel_%"].first().to_dict()
    rel_rows, full_rows, pred_frames = [], [], []

    for test_year, train_years in FOLDS.items():
        tr = df[df["Year"].isin(train_years)]
        te = df[df["Year"] == test_year]
        role = "test" if test_year == TEST_FOLD else "validation"
        pf = te[["MuniCode", "Year", "Turnout_%", TARGET, "PreviousRelative_pts",
                 "PreviousTurnout_%"]].copy()
        for name, fn in relative_models().items():
            rel_pred = fn(tr, te)
            pf[f"Rel|{name}"] = rel_pred
            rel_rows.append({"TestYear": test_year, "Role": role, "Model": name,
                             "TrainYears": ",".join(map(str, train_years)),
                             **metrics(te[TARGET], rel_pred)})
            for lname, lfn in level_methods().items():
                level = lfn(levels, train_years, test_year)
                full = np.clip(level + rel_pred, 0, 100)
                full_rows.append({"TestYear": test_year, "Role": role, "RelativeModel": name,
                                  "LevelMethod": lname, "AssumedLevel": level,
                                  "ActualLevel": levels[test_year],
                                  **metrics(te["Turnout_%"], full)})
                if lname == "Previous level":
                    pf[f"Full|{name}"] = full
        pred_frames.append(pf)

    return pd.DataFrame(rel_rows), pd.DataFrame(full_rows), pd.concat(pred_frames, ignore_index=True)


def select_relative_model(relative_scores: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Pre-declared rule: lowest mean MAE over the validation folds only."""
    val = (relative_scores[relative_scores["Role"] == "validation"]
           .groupby("Model", as_index=False)["MAE"].mean()
           .rename(columns={"MAE": "MeanValidationMAE"})
           .sort_values("MeanValidationMAE"))
    return val.iloc[0]["Model"], val.reset_index(drop=True)


def supplementary_census_check(master: pd.DataFrame) -> pd.DataFrame:
    """Does Census information (as known before the vote) add predictive value?

    Census 2011 is the latest census published before the 2016 and 2021 elections,
    so a model with demographic inputs can only be trained on the 2016 target and
    tested on 2021. It is therefore reported as a supplementary check, not as a
    candidate for selection.
    """
    df = modelling_frame(master).dropna(subset=KNOWN_DEMOGRAPHICS)
    tr, te = df[df["Year"] == 2016], df[df["Year"] == 2021]
    rows = []
    for label, feats in [("Electoral history only", FEATURES),
                         ("Electoral history + Census 2011", FEATURES + KNOWN_DEMOGRAPHICS),
                         ("Census 2011 only", KNOWN_DEMOGRAPHICS)]:
        pred = _ridge().fit(tr[feats], tr[TARGET]).predict(te[feats])
        rows.append({"Inputs": label, "TrainTarget": 2016, "TestYear": 2021, **metrics(te[TARGET], pred)})
    rows.append({"Inputs": "Relative persistence (reference)", "TrainTarget": 2016, "TestYear": 2021,
                 **metrics(te[TARGET], te["PreviousRelative_pts"])})
    return pd.DataFrame(rows)


def error_band(predictions: pd.DataFrame, model: str, q: float = 0.8) -> dict:
    """Empirical error scale of the relative component across all folds."""
    err = (predictions[TARGET] - predictions[f"Rel|{model}"]).abs()
    by_year = predictions.assign(err=err).groupby("Year")["err"].mean().to_dict()
    return {"q": q, "abs_error_quantile": float(err.quantile(q)), "mae_all_folds": float(err.mean()),
            "mae_by_fold": by_year}
