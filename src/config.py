"""Project-wide constants and paths.

Every notebook, test and the dashboard import from here so that municipality
codes, party categories, file locations and colours are defined exactly once.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ----------------------------------------------------------------------------
# Directories
# ----------------------------------------------------------------------------
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"

DIRS = {
    "phase1": PROCESSED / "elections" / "phase1",
    "phase2": PROCESSED / "demographics" / "phase2",
    "phase3": PROCESSED / "panels" / "phase3",
    "phase4": PROCESSED / "models" / "phase4",
    "phase5": PROCESSED / "models" / "phase5",
    "phase6": PROCESSED / "scenarios" / "phase6",
    "legacy": PROCESSED / "legacy_prototype",
}

# ----------------------------------------------------------------------------
# Raw inputs
# ----------------------------------------------------------------------------
ELECTION_YEARS = [2000, 2006, 2011, 2016, 2021]

RAW_ELECTION_FILES = {
    2000: RAW / "detailed" / "2000 LGE.csv",
    2006: RAW / "detailed" / "2006 LGE.csv",
    2011: RAW / "detailed" / "2011_detailed" / "EC.csv",
    2016: RAW / "detailed" / "2016_detailed" / "EC.csv",
    2021: RAW / "detailed" / "2021_detailed" / "EC.csv",
}

# Official IEC "Voter Turnout Report" spreadsheets, used only for independent
# validation of the turnout we reconstruct from the detailed results.
IEC_TURNOUT_REPORTS = {
    2000: RAW / "turnout" / "2000 turnout.xls",          # province level
    2006: RAW / "turnout" / "2006_turnout.xls",          # province level
    2011: RAW / "turnout" / "2011_turnout.xls",          # province level
    2016: RAW / "turnout" / "2016" / "EC.xls",           # municipality level
    2021: RAW / "turnout" / "2021" / "EC.xls",           # municipality level
}

MUNICIPAL_CENSUS = PROCESSED / "demographics" / "clean_census.csv"
# NOTE: despite its name, this file is a Buffalo City (BUF) age x sex x population-group
# table for Census 1996/2001/2011/2022: its 2022 total (975 255) equals BUF's 2022
# population exactly. It is NOT a provincial table.
BUF_AGE_SEX_CENSUS = EXTERNAL / "demographics" / "EC CENSUS.csv"
REGISTRATION_2026 = RAW / "registration" / "ec_registration_2026.csv"  # optional

RAW_TOPOJSON = RAW / "geo" / "za-local.topojson"
GEOJSON = EXTERNAL / "geo" / "ec_municipalities_33.geojson"

# ----------------------------------------------------------------------------
# Geography
# ----------------------------------------------------------------------------
# Historical code -> current analytical code. Mergers effective from the
# 2016 LGE (MDB 2016 re-determination) plus the 2006 cross-boundary changes.
CODE_MAP = {
    "EC103": "EC101",  # Ikwezi        -> Dr Beyers Naude
    "EC107": "EC101",  # Baviaans      -> Dr Beyers Naude
    "EC125": "BUF",    # Buffalo City local (2000/2006) -> Buffalo City metro
    "EC127": "EC129",  # Nkonkobe      -> Raymond Mhlaba
    "EC128": "EC129",  # Nxuba         -> Raymond Mhlaba
    "EC132": "EC139",  # Tsolwana      -> Enoch Mgijima
    "EC133": "EC139",  # Inkwanca      -> Enoch Mgijima
    "EC134": "EC139",  # Lukanji       -> Enoch Mgijima
    "EC143": "EC145",  # Maletswai     -> Walter Sisulu
    "EC144": "EC145",  # Gariep        -> Walter Sisulu
    "EC151": "EC443",  # Mbizana (2000 code) -> Winnie Madikizela-Mandela
    "EC152": "EC444",  # Ntabankulu (2000 code)
    "EC05B2": "EC442", # Umzimvubu (2000/2006 cross-boundary code)
    "EC05B3": "EC441", # Matatiele (2006 cross-boundary code; in KwaZulu-Natal in 2000)
}
# Excluded on purpose: EC05B1 Umzimkulu (EC in 2000, transferred to KwaZulu-Natal
# in 2006) and the District Management Areas (ECDMA*), which elected only district
# councils. Hence 32 municipalities in 2000 (no Matatiele yet) and 33 afterwards.

MUNICIPALITY_NAMES = {
    "BUF": "Buffalo City", "NMA": "Nelson Mandela Bay",
    "EC101": "Dr Beyers Naude", "EC102": "Blue Crane Route", "EC104": "Makana",
    "EC105": "Ndlambe", "EC106": "Sundays River Valley", "EC108": "Kouga",
    "EC109": "Kou-Kamma", "EC121": "Mbhashe", "EC122": "Mnquma",
    "EC123": "Great Kei", "EC124": "Amahlathi", "EC126": "Ngqushwa",
    "EC129": "Raymond Mhlaba", "EC131": "Inxuba Yethemba", "EC135": "Intsika Yethu",
    "EC136": "Emalahleni", "EC137": "Engcobo", "EC138": "Sakhisizwe",
    "EC139": "Enoch Mgijima", "EC141": "Elundini", "EC142": "Senqu",
    "EC145": "Walter Sisulu", "EC153": "Ngquza Hill", "EC154": "Port St Johns",
    "EC155": "Nyandeni", "EC156": "Mhlontlo", "EC157": "King Sabata Dalindyebo",
    "EC441": "Matatiele", "EC442": "Umzimvubu",
    "EC443": "Winnie Madikizela-Mandela", "EC444": "Ntabankulu",
}
TARGET_CODES = set(MUNICIPALITY_NAMES)

DISTRICTS = {
    "BUF": "Buffalo City (metro)", "NMA": "Nelson Mandela Bay (metro)",
    **{c: "Sarah Baartman" for c in ["EC101", "EC102", "EC104", "EC105", "EC106", "EC108", "EC109"]},
    **{c: "Amathole" for c in ["EC121", "EC122", "EC123", "EC124", "EC126", "EC129"]},
    **{c: "Chris Hani" for c in ["EC131", "EC135", "EC136", "EC137", "EC138", "EC139"]},
    **{c: "Joe Gqabi" for c in ["EC141", "EC142", "EC145"]},
    **{c: "O.R. Tambo" for c in ["EC153", "EC154", "EC155", "EC156", "EC157"]},
    **{c: "Alfred Nzo" for c in ["EC441", "EC442", "EC443", "EC444"]},
}

# ----------------------------------------------------------------------------
# Parties
# ----------------------------------------------------------------------------
NAMED_PARTIES = ["ANC", "DA", "EFF", "UDM", "ATM"]
PARTIES = NAMED_PARTIES + ["OTHER"]

PARTY_COLORS = {
    "ANC": "#1B7A3E", "DA": "#1F5BA8", "EFF": "#B3202A",
    "UDM": "#D9A21B", "ATM": "#6C4F9E", "OTHER": "#8C8C8C",
}

# ----------------------------------------------------------------------------
# Project palette (Eastern Cape: Wild Coast water, aloe flower, grassland)
# ----------------------------------------------------------------------------
INK = "#1E2B2F"
TEAL = "#0E5E5A"
TEAL_LIGHT = "#7FB5AE"
ALOE = "#D2542B"
GRASS = "#A3B18A"
MIST = "#EEF3F1"
GREY = "#8C8C8C"


def muni_name(code: str) -> str:
    """Human-readable municipality name for an analytical code."""
    return MUNICIPALITY_NAMES.get(code, code)


def ensure_dirs() -> None:
    for d in DIRS.values():
        d.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
