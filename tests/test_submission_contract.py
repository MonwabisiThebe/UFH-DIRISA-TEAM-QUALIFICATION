from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def test_core_outputs_exist():
    assert (ROOT/'data/processed/elections/phase1/municipality_election_panel_2000_2021.csv').exists()
    assert (ROOT/'data/processed/scenarios/phase6/municipality_scenarios_2026.csv').exists()
def test_election_panel_contract():
    p=ROOT/'data/processed/elections/phase1/municipality_election_panel_2000_2021.csv'
    if not p.exists(): return
    d=pd.read_csv(p); assert len(d)==164; assert d[['MuniCode','Year']].duplicated().sum()==0
def test_scenario_contract():
    p=ROOT/'data/processed/scenarios/phase6/municipality_scenarios_2026.csv'
    if not p.exists(): return
    d=pd.read_csv(p); assert d.MuniCode.nunique()==33; assert d['TurnoutScenario_2026'].between(0,100).all()
