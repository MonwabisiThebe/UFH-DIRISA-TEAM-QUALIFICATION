"""Unit tests for the core calculations, using small hand-checkable inputs."""
import numpy as np
import pandas as pd
import pytest

from src.data.elections import extract_historical_code, harmonise_code, normalise_party_name, process_election
from src.models.evaluation import metrics
from src.models.party import compose
from src.models.scenarios import apply_swing, leaders


def test_code_extraction_and_harmonisation():
    assert extract_historical_code("EC104 - Makana [Grahamstown]") == "EC104"
    assert extract_historical_code("ECDMA10 - Aberdeen Plain") is None
    assert harmonise_code("EC133 - Inkwanca [Molteno]") == "EC139"
    assert harmonise_code("Port Elizabeth [Nelson Mandela]") == "NMA"


def test_party_normalisation():
    assert normalise_party_name("AFRICAN NATIONAL CONGRESS") == "ANC"
    assert normalise_party_name("DEMOCRATIC ALLIANCE/DEMOKRATIESE ALLIANSIE") == "DA"
    assert normalise_party_name("Some Local Forum") == "Some Local Forum"


def _toy_new_schema():
    # Two voting districts, two parties, PR + ward rows; registered/spoilt repeat per party row.
    rows = []
    for vd, reg, spoilt, votes in [("VD1", 100, 2, {"AFRICAN NATIONAL CONGRESS": 40, "DEMOCRATIC ALLIANCE": 10}),
                                   ("VD2", 200, 4, {"AFRICAN NATIONAL CONGRESS": 60, "DEMOCRATIC ALLIANCE": 40})]:
        for party, v in votes.items():
            for ballot in ["PR", "Ward"]:
                rows.append({"Province": "Eastern Cape", "Municipality": "EC104 - Makana", "Ward": 1,
                             "VotingDistrict": vd, "RegisteredVoters": reg, "BallotType": ballot,
                             "SpoiltVotes": spoilt, "PartyName": party, "TotalValidVotes": v})
    return pd.DataFrame(rows)


def test_process_election_deduplicates_and_computes_metrics():
    out = process_election(2016, _toy_new_schema())
    m = out["municipality"].iloc[0]
    assert m["RegisteredVoters"] == 300          # not 600: counted once per voting district
    assert m["SpoiltVotes"] == 6
    assert m["ValidVotes"] == 150                # PR rows only
    assert m["Turnout_%"] == pytest.approx(100 * 156 / 300)
    comp = out["competition"].iloc[0]
    shares = np.array([100 / 150, 50 / 150])     # ANC 100, DA 50
    assert comp["ENP"] == pytest.approx(1 / np.sum(shares ** 2))
    assert comp["Margin_pts"] == pytest.approx(100 * (100 - 50) / 150)


def test_metrics_and_bias_sign():
    r = metrics([50, 60], [52, 62])
    assert r["MAE"] == pytest.approx(2) and r["Bias"] == pytest.approx(2)


def test_compose_clips_and_renormalises():
    out = compose(np.array([[60.0, 50.0, -5.0]]))
    assert np.allclose(out.sum(axis=1), 100) and (out >= 0).all()


def test_swing_and_leaders():
    base = pd.DataFrame({"MuniCode": ["A"], "ANC": [40.0], "DA": [39.0], "EFF": [10.0], "UDM": [5.0], "ATM": [3.0], "OTHER": [3.0]})
    swung = apply_swing(base, {"ANC": -1.0, "DA": 1.0})
    assert swung.loc[0, "DA"] > swung.loc[0, "ANC"]
    L = leaders(base, close_threshold=5)
    assert L.loc[0, "Leader"] == "ANC" and bool(L.loc[0, "TooCloseToCall"])
