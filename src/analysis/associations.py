"""Turnout associations that are robust to election-wide shocks.

Pooling 2011, 2016 and 2021 and correlating raw turnout with a variable mixes two
different things: differences *between municipalities* and differences *between
elections*. Because turnout fell in every municipality in 2021 while the number of
contesting parties (and interpolated service access) rose, pooled correlations can
take the wrong sign (Simpson's paradox). We therefore report:

* within-election correlations (one per year, n = 33, with Fisher 95% CIs);
* year-demeaned ("fixed-effects") correlations across 2011-2021 (n = 99);
* an OLS model with election fixed effects and municipality-clustered errors.

All results are municipality-level associations, not causal or individual-level
effects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _fisher_ci(r: float, n: int, z: float = 1.96):
    if n <= 3 or not np.isfinite(r):
        return np.nan, np.nan
    zr = np.arctanh(np.clip(r, -0.999999, 0.999999))
    se = 1 / np.sqrt(n - 3)
    return float(np.tanh(zr - z * se)), float(np.tanh(zr + z * se))


def association_table(df: pd.DataFrame, variables, target="Turnout_%",
                      years=(2011, 2016, 2021)) -> pd.DataFrame:
    """Pooled vs within-election vs year-demeaned correlations with turnout."""
    d = df[df["Year"].isin(years)].copy()
    rows = []
    for v in variables:
        sub = d.dropna(subset=[v, target])
        rec = {"Variable": v, "Pooled_r": sub[v].corr(sub[target])}
        for y in years:
            s = sub[sub["Year"] == y]
            r = s[v].corr(s[target])
            lo, hi = _fisher_ci(r, len(s))
            rec[f"r_{y}"], rec[f"r_{y}_lo"], rec[f"r_{y}_hi"] = r, lo, hi
        dv = sub[v] - sub.groupby("Year")[v].transform("mean")
        dt = sub[target] - sub.groupby("Year")[target].transform("mean")
        r = dv.corr(dt)
        rec["WithinYear_r"] = r
        rec["WithinYear_lo"], rec["WithinYear_hi"] = _fisher_ci(r, len(sub) - len(years))
        rec["SignFlip"] = np.sign(rec["Pooled_r"]) != np.sign(r)
        rows.append(rec)
    return pd.DataFrame(rows)


def fixed_effects_regression(df: pd.DataFrame, predictors, target="Turnout_%",
                             years=(2011, 2016, 2021)):
    """OLS of turnout on standardised predictors + election dummies.

    Standard errors are clustered by municipality (each municipality appears up
    to three times). Returns (statsmodels result, tidy coefficient table).
    """
    import statsmodels.formula.api as smf

    d = df[df["Year"].isin(years)].dropna(subset=list(predictors) + [target]).copy()
    names = {}
    for v in predictors:
        safe = "z_" + "".join(ch if ch.isalnum() else "_" for ch in v)
        d[safe] = (d[v] - d[v].mean()) / d[v].std()
        names[safe] = v
    d["y"] = d[target]
    formula = "y ~ " + " + ".join(names) + " + C(Year)"
    res = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["MuniCode"]})
    ci = res.conf_int()
    tidy = pd.DataFrame({
        "Variable": [names[k] for k in names],
        "Coef_pts_per_SD": [res.params[k] for k in names],
        "CI_low": [ci.loc[k, 0] for k in names],
        "CI_high": [ci.loc[k, 1] for k in names],
        "p_value": [res.pvalues[k] for k in names],
    })
    return res, tidy


def vif_table(df: pd.DataFrame, predictors) -> pd.DataFrame:
    """Variance inflation factors, to keep the regression free of redundant inputs."""
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    X = df[list(predictors)].dropna()
    X = (X - X.mean()) / X.std()
    X.insert(0, "const", 1.0)
    return pd.DataFrame({"Variable": predictors,
                         "VIF": [variance_inflation_factor(X.values, i + 1) for i in range(len(predictors))]})


def turnout_persistence(master: pd.DataFrame) -> pd.DataFrame:
    """How strongly does a municipality's turnout/relative position carry over?"""
    rows = []
    for y in sorted(master["Year"].unique()):
        s = master[(master["Year"] == y) & master["PreviousTurnout_%"].notna()]
        if s.empty:
            continue
        rows.append({
            "Transition": f"{ {2006: 2000, 2011: 2006, 2016: 2011, 2021: 2016}[y] }->{y}",
            "TargetYear": y, "n": len(s),
            "r_turnout": s["Turnout_%"].corr(s["PreviousTurnout_%"]),
            "r_relative": s["RelativeTurnout_pts"].corr(s["PreviousRelative_pts"]),
            "MeanChange_pts": (s["Turnout_%"] - s["PreviousTurnout_%"]).mean(),
            "SD_change_pts": (s["Turnout_%"] - s["PreviousTurnout_%"]).std(),
        })
    return pd.DataFrame(rows)


def year_only_r2(df: pd.DataFrame, target="Turnout_%", years=(2011, 2016, 2021)) -> float:
    """R^2 of turnout on election-year dummies alone (the province-wide component)."""
    d = df[df["Year"].isin(years)].dropna(subset=[target])
    fitted = d.groupby("Year")[target].transform("mean")
    return float(1 - ((d[target] - fitted) ** 2).sum() / ((d[target] - d[target].mean()) ** 2).sum())
