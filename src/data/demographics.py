"""Municipal Census context and its alignment to election years.

Two alignment policies are used, deliberately, for two different jobs:

``descriptive``  (Phase 3 EDA)
    2011 = Census 2011; 2016/2021 = linear interpolation between Census 2011 and
    Census 2022; 2000/2006 = missing (no back-extrapolation). Good for describing
    each election, but the 2016/2021 values use a 2022 endpoint.

``as_known``  (Phase 4-6 prediction)
    Only a census already *published before the election* may be used:
    Census 2011 (released Oct 2012) for the 2016 and 2021 elections, Census 2022
    (released Oct 2023) for 2026. Nothing for 2000-2011 targets in this dataset.
    This is the leakage-safe policy.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import MUNICIPAL_CENSUS, TARGET_CODES

METRICS = ["Pop", "U15", "O65", "Med", "NoSch", "Matric", "Higher", "Formal", "Water", "Elec"]

FEATURE_LABELS = {
    "Pop": "Population",
    "U15": "Population aged under 15 (%)",
    "O65": "Population aged 65+ (%)",
    "Med": "Median age (years)",
    "NoSch": "Adults with no schooling (%)",
    "Matric": "Adults with matric (%)",
    "Higher": "Adults with higher education (%)",
    "Formal": "Households in formal dwellings (%)",
    "Water": "Households with piped water (%)",
    "Elec": "Households with electricity (%)",
}

# Census edition legitimately available before each election (as_known policy).
CENSUS_AVAILABLE_FOR = {2016: 2011, 2021: 2011, 2026: 2022}


def load_census(path=MUNICIPAL_CENSUS) -> pd.DataFrame:
    """Wide 33-row table with ``<metric>_2011`` and ``<metric>_2022`` columns."""
    c = pd.read_csv(path)
    assert set(c["MuniCode"]) == TARGET_CODES, "Census table must cover the 33 municipalities"
    return c


def align_descriptive(census: pd.DataFrame, years=(2000, 2006, 2011, 2016, 2021)) -> pd.DataFrame:
    """Election-year demographics for description (interpolated 2016/2021)."""
    rows = []
    for _, r in census.iterrows():
        for y in years:
            rec = {"MuniCode": r["MuniCode"], "Year": y}
            if y < 2011:
                rec.update({m: np.nan for m in METRICS})
                rec["DemographicStatus"] = "Unavailable_pre2011"
            elif y == 2011:
                rec.update({m: r[f"{m}_2011"] for m in METRICS})
                rec["DemographicStatus"] = "Observed_Census2011"
            else:
                a = (y - 2011) / 11.0
                rec.update({m: r[f"{m}_2011"] + a * (r[f"{m}_2022"] - r[f"{m}_2011"]) for m in METRICS})
                rec["DemographicStatus"] = "Interpolated_2011_2022"
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(["MuniCode", "Year"]).reset_index(drop=True)


def align_as_known(census: pd.DataFrame, years=(2000, 2006, 2011, 2016, 2021, 2026)) -> pd.DataFrame:
    """Election-year demographics using only censuses published before the vote."""
    rows = []
    for _, r in census.iterrows():
        for y in years:
            src = CENSUS_AVAILABLE_FOR.get(y)
            rec = {"MuniCode": r["MuniCode"], "Year": y, "CensusUsed": src or "none"}
            rec.update({f"K_{m}": (r[f"{m}_{src}"] if src else np.nan) for m in METRICS})
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(["MuniCode", "Year"]).reset_index(drop=True)


def current_profile(census: pd.DataFrame) -> pd.DataFrame:
    """Census 2022 snapshot plus 2011->2022 change, for profiles and context."""
    out = census[["MuniCode"]].copy()
    for m in METRICS:
        out[m] = census[f"{m}_2022"]
        out[f"{m}_change_2011_2022"] = census[f"{m}_2022"] - census[f"{m}_2011"]
    out["PopGrowth_%"] = 100 * (census["Pop_2022"] / census["Pop_2011"] - 1)
    return out
