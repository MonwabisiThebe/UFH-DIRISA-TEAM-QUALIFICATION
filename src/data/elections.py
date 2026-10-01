"""Raw IEC Local Government Election results -> harmonised municipal tables.

Two IEC schema generations exist:

* 2000/2006: ``Voting District``, ``Party``, ``Ballot Type``, ``Registered Voters``,
  ``Valid Votes Cast`` (party-row votes), ``Spoilt Votes`` ...
* 2011/2016/2021: ``VotingDistrict``, ``PartyName``, ``BallotType``,
  ``RegisteredVoters``, ``TotalValidVotes`` (party-row votes), ``SpoiltVotes`` ...

In both, registered voters and spoilt ballots are repeated on every party row of a
voting district, so they are de-duplicated per voting district before summing,
while party votes are summed over all party rows.

Only the PR ballot is used, so party support is measured on the same ballot in
every election.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.config import CODE_MAP, NAMED_PARTIES, RAW_ELECTION_FILES, TARGET_CODES


# ----------------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------------
def read_election_file(year: int, path=None) -> pd.DataFrame:
    """Read one raw IEC detailed-results CSV with the right text encoding.

    The 2011 file is UTF-16; the others are UTF-8 (with BOM) or Latin-1.
    Column names are whitespace-normalised.
    """
    path = path or RAW_ELECTION_FILES[year]
    encodings = ["utf-16"] if year == 2011 else ["utf-8-sig", "latin1"]
    last_error = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
            return df
        except UnicodeDecodeError as exc:  # try the next encoding
            last_error = exc
    raise last_error


def numeric(series: pd.Series) -> pd.Series:
    """Parse numbers stored as text (thousand separators, % signs)."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )


# ----------------------------------------------------------------------------
# Harmonisation
# ----------------------------------------------------------------------------
def extract_historical_code(value) -> str | None:
    """'EC104 - Makana' -> 'EC104'. Returns None for District Management Areas."""
    text = str(value).strip()
    if text.upper().startswith("PORT ELIZABETH"):  # 2000 label for Nelson Mandela Bay
        return "NMA"
    code = text.split(" - ")[0].strip().upper()
    if code.startswith("ECDMA"):  # DMAs are not present-day local municipalities
        return None
    return code


def harmonise_code(value) -> str | None:
    """Map a raw municipality label to the 33-unit analytical geography."""
    code = extract_historical_code(value)
    return None if code is None else CODE_MAP.get(code, code)


def normalise_party_name(value) -> str:
    """Collapse spelling variants of the five named parties to short labels."""
    name = str(value).strip()
    upper = name.upper()
    if upper == "AFRICAN NATIONAL CONGRESS":
        return "ANC"
    if "DEMOCRATIC ALLIANCE" in upper or "DEMOKRATIESE ALLIANSIE" in upper:
        return "DA"
    if upper == "ECONOMIC FREEDOM FIGHTERS":
        return "EFF"
    if upper == "UNITED DEMOCRATIC MOVEMENT":
        return "UDM"
    if upper == "AFRICAN TRANSFORMATION MOVEMENT":
        return "ATM"
    return name


# ----------------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------------
def process_election(year: int, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Aggregate one election's raw rows to municipality level (PR ballot).

    Returns a dict with ``municipality`` (turnout facts), ``party`` (votes and
    shares per party, full distribution), ``competition`` (top share, margin,
    ENP, party count) and ``dropped`` (raw units outside the analytical geography).
    """
    x = df[df["Province"].astype(str).str.strip().str.casefold().eq("eastern cape")].copy()

    if year <= 2006:
        vd_col, party_col, ballot_col = "Voting District", "Party", "Ballot Type"
        reg, spoilt, votes = "Registered Voters", "Spoilt Votes", "Valid Votes Cast"
    else:
        vd_col, party_col, ballot_col = "VotingDistrict", "PartyName", "BallotType"
        reg, spoilt, votes = "RegisteredVoters", "SpoiltVotes", "TotalValidVotes"

    x = x[x[ballot_col].astype(str).str.strip().str.upper().eq("PR")].copy()
    x["RegisteredVoters"] = numeric(x[reg])
    x["SpoiltVotes"] = numeric(x[spoilt])
    x["PartyVotes"] = numeric(x[votes])
    x["HistoricalCode"] = x["Municipality"].map(extract_historical_code)
    x["MuniCode"] = x["Municipality"].map(harmonise_code)
    x["Party"] = x[party_col].map(normalise_party_name)

    dropped = (x.loc[~x["MuniCode"].isin(TARGET_CODES), ["Municipality", "HistoricalCode"]]
               .drop_duplicates().assign(Year=year))
    x = x[x["MuniCode"].isin(TARGET_CODES)].copy()

    # Voting-district facts repeat on each party row: count them once.
    district = x.drop_duplicates(["MuniCode", vd_col])
    muni = district.groupby("MuniCode", as_index=False).agg(
        RegisteredVoters=("RegisteredVoters", "sum"),
        SpoiltVotes=("SpoiltVotes", "sum"),
        VotingDistricts=(vd_col, "nunique"),
    )

    party = x.groupby(["MuniCode", "Party"], as_index=False).agg(PartyVotes=("PartyVotes", "sum"))
    valid = party.groupby("MuniCode", as_index=False).agg(ValidVotes=("PartyVotes", "sum"))

    muni = muni.merge(valid, on="MuniCode", how="left")
    muni["VotesCast"] = muni["ValidVotes"] + muni["SpoiltVotes"]
    muni["Turnout_%"] = 100 * muni["VotesCast"] / muni["RegisteredVoters"]
    muni["SpoiltRate_%"] = 100 * muni["SpoiltVotes"] / muni["VotesCast"]
    muni["Year"] = year

    party = party.merge(valid, on="MuniCode", how="left")
    party["VoteShare_%"] = 100 * party["PartyVotes"] / party["ValidVotes"]
    party["Year"] = year

    # Competition is computed from the COMPLETE party distribution (before grouping).
    rows = []
    for code, g in party.groupby("MuniCode"):
        s = np.sort(g["VoteShare_%"].to_numpy(dtype=float))[::-1]
        rows.append({
            "MuniCode": code, "Year": year,
            "TopShare_%": s[0],
            "Margin_pts": s[0] - s[1] if len(s) > 1 else s[0],
            "ENP": 1.0 / np.sum((s / 100.0) ** 2),
            "NumberOfParties": int((s > 0).sum()),
        })
    competition = pd.DataFrame(rows)
    return {"municipality": muni, "party": party, "competition": competition, "dropped": dropped}


def add_lags(panel: pd.DataFrame) -> pd.DataFrame:
    """Previous-election values and changes, computed within municipality."""
    p = panel.sort_values(["MuniCode", "Year"]).copy()
    g = p.groupby("MuniCode")
    for col, new in [("RegisteredVoters", "PreviousRegisteredVoters"),
                     ("Turnout_%", "PreviousTurnout_%"), ("ENP", "PreviousENP"),
                     ("Margin_pts", "PreviousMargin_pts"), ("TopShare_%", "PreviousTopShare_%"),
                     ("NumberOfParties", "PreviousNumberOfParties")]:
        p[new] = g[col].shift(1)
    p["TurnoutChange_pts"] = p["Turnout_%"] - p["PreviousTurnout_%"]
    p["ENPChange"] = p["ENP"] - p["PreviousENP"]
    p["MarginChange_pts"] = p["Margin_pts"] - p["PreviousMargin_pts"]
    p["RegistrationGrowth_%"] = 100 * (p["RegisteredVoters"] / p["PreviousRegisteredVoters"] - 1)
    return p.reset_index(drop=True)


def build_election_tables(raw: dict[int, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Run :func:`process_election` for every year and assemble the panel tables."""
    results = {y: process_election(y, df) for y, df in sorted(raw.items())}

    panel = pd.concat([r["municipality"] for r in results.values()], ignore_index=True)
    competition = pd.concat([r["competition"] for r in results.values()], ignore_index=True)
    party_long = (pd.concat([r["party"] for r in results.values()], ignore_index=True)
                  .sort_values(["Year", "MuniCode", "Party"]).reset_index(drop=True))
    dropped = pd.concat([r["dropped"] for r in results.values()], ignore_index=True)

    panel = panel.merge(competition, on=["MuniCode", "Year"], validate="one_to_one")
    panel = add_lags(panel)

    wide = (party_long[party_long["Party"].isin(NAMED_PARTIES)]
            .pivot_table(index=["Year", "MuniCode"], columns="Party", values="VoteShare_%",
                         aggfunc="sum", fill_value=0.0).reset_index())
    wide.columns.name = None
    for p in NAMED_PARTIES:
        if p not in wide:
            wide[p] = 0.0
    # Every municipality-year must be present even if no named party contested.
    keys = panel[["Year", "MuniCode"]]
    wide = keys.merge(wide, on=["Year", "MuniCode"], how="left").fillna(0.0)
    wide["OTHER"] = (100.0 - wide[NAMED_PARTIES].sum(axis=1)).clip(lower=0.0)
    wide = wide[["Year", "MuniCode", *NAMED_PARTIES, "OTHER"]].sort_values(["MuniCode", "Year"])

    return {"panel": panel, "party_long": party_long,
            "party_wide": wide.reset_index(drop=True),
            "competition": competition, "dropped": dropped}


# ----------------------------------------------------------------------------
# Official IEC turnout reports (independent validation source)
# ----------------------------------------------------------------------------
def read_iec_turnout_report(path) -> pd.DataFrame:
    """Parse an IEC 'Voter Turnout Report' .xls into a tidy table.

    The IEC defines % turnout as (highest of ward or PR votes cast) /
    (registered voters + MEC7 special votes). Rows are municipalities in the
    2016/2021 reports and provinces in the 2000/2006/2011 reports.
    """
    import os

    import xlrd

    # xlrd warns about padding in IEC-exported .xls files; the content is fine.
    with open(os.devnull, "w") as devnull:
        book = xlrd.open_workbook(str(path), logfile=devnull)
    raw = pd.read_excel(book, header=None, engine="xlrd")
    raw = raw.dropna(how="all").dropna(how="all", axis=1)
    rows = []
    for _, r in raw.iterrows():
        vals = [v for v in r.tolist() if pd.notna(v)]
        if len(vals) < 4 or not isinstance(vals[0], str):
            continue
        nums = [v for v in vals[1:] if isinstance(v, (int, float, np.integer, np.floating))]
        if len(nums) < 3 or not (0 < nums[-1] <= 1):
            continue
        # Layouts differ by year, but the first number is always registered
        # voters and the last is the turnout fraction. (In 2006 the middle
        # columns count votes across all ballots, so only these two are used.)
        rows.append({"Unit": vals[0].strip(), "RegisteredVoters": nums[0],
                     "Turnout_%": 100 * nums[-1]})
    out = pd.DataFrame(rows)
    out["MuniCode"] = out["Unit"].map(lambda s: harmonise_code(s) if " - " in s else None)
    return out
