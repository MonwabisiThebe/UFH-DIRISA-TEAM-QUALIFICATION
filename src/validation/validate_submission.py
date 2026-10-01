from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
P={
'elections':ROOT/'data/processed/elections/phase1/municipality_election_panel_2000_2021.csv',
'party':ROOT/'data/processed/elections/phase1/party_shares_selected_wide_2000_2021.csv',
'analysis':ROOT/'data/processed/panels/phase3/analysis_panel_2011_2021.csv',
'turnout_eval':ROOT/'data/processed/models/phase4/turnout_model_comparison_2021.csv',
'party_eval':ROOT/'data/processed/models/phase5/party_support_model_comparison_2021.csv',
'scenario':ROOT/'data/processed/scenarios/phase6/municipality_scenarios_2026.csv'}

def run():
    missing=[str(v.relative_to(ROOT)) for v in P.values() if not v.exists()]
    assert not missing, f'Missing outputs: {missing}'
    e=pd.read_csv(P['elections']); s=pd.read_csv(P['scenario'])
    assert len(e)==164
    assert e[['MuniCode','Year']].duplicated().sum()==0
    assert set(e.Year.unique())=={2000,2006,2011,2016,2021}
    assert e.Turnout_.between(0,100).all() if 'Turnout_' in e else e['Turnout_%'].between(0,100).all()
    assert s.MuniCode.nunique()==33
    assert s['TurnoutScenario_2026'].between(0,100).all()
    party_cols=[c for c in s if c.endswith('_Scenario_2026') and c!='TurnoutScenario_2026']
    assert np.allclose(s[party_cols].sum(axis=1),100,atol=0.05)
    print('Submission validation passed.')
if __name__=='__main__': run()
