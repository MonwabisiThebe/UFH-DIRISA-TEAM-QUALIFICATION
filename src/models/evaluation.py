"""Shared evaluation metrics (all in percentage points where applicable)."""
from __future__ import annotations

import numpy as np


def metrics(y_true, y_pred) -> dict:
    """MAE, RMSE, R^2, bias (mean prediction error) and Pearson r."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_pred, dtype=float)
    err = p - y
    ss_res = float(np.sum((y - p) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r = float(np.corrcoef(y, p)[0, 1]) if np.std(p) > 0 and np.std(y) > 0 else np.nan
    return {
        "MAE": float(np.mean(np.abs(err))),
        "RMSE": float(np.sqrt(np.mean(err ** 2))),
        "R2": 1 - ss_res / ss_tot if ss_tot > 0 else np.nan,
        "Bias": float(np.mean(err)),
        "r": r,
        "n": int(len(y)),
    }
