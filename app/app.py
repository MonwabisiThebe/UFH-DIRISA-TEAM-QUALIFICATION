from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------- PAGE ---------------------------------
st.set_page_config(
    page_title="EC Electoral Dynamics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px;}
[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 12px;
    padding: 14px 16px;
}
[data-testid="stMetricLabel"] {font-size: .86rem;}
.small-note {opacity:.76; font-size:.88rem;}
.section-note {
    padding:.75rem 1rem; border-left:4px solid #888;
    background:rgba(128,128,128,.08); border-radius:4px;
}
.hero {
    padding:1.1rem 1.25rem; border:1px solid rgba(128,128,128,.2);
    border-radius:14px; margin-bottom:1rem;
}
</style>
""", unsafe_allow_html=True)

PARTIES = ["ANC", "DA", "EFF", "UDM", "ATM", "OTHER"]
MUNICIPALITIES = {
"BUF":"Buffalo City","EC101":"Dr Beyers Naude","EC102":"Blue Crane Route",
"EC104":"Makana","EC105":"Ndlambe","EC106":"Sundays River Valley",
"EC108":"Kouga","EC109":"Kou-Kamma","EC121":"Mbhashe","EC122":"Mnquma",
"EC123":"Great Kei","EC124":"Amahlathi","EC126":"Ngqushwa",
"EC129":"Raymond Mhlaba","EC131":"Inxuba Yethemba","EC135":"Intsika Yethu",
"EC136":"Emalahleni","EC137":"Engcobo","EC138":"Sakhisizwe",
"EC139":"Enoch Mgijima","EC141":"Elundini","EC142":"Senqu",
"EC145":"Walter Sisulu","EC153":"Ngquza Hill","EC154":"Port St Johns",
"EC155":"Nyandeni","EC156":"Mhlontlo","EC157":"King Sabata Dalindyebo",
"EC441":"Matatiele","EC442":"Umzimvubu","EC443":"Winnie Madikizela-Mandela",
"EC444":"Ntabankulu","NMA":"Nelson Mandela Bay"
}

def project_root():
    starts = [Path(__file__).resolve().parent, Path.cwd().resolve()]
    for start in starts:
        for p in [start, *start.parents]:
            if (p/"data").exists():
                return p
    raise FileNotFoundError("Repository root with data/ folder could not be located.")

ROOT = project_root()
PATHS = {
"elections": ROOT/"data/processed/elections/phase1/municipality_election_panel_2000_2021.csv",
"party": ROOT/"data/processed/elections/phase1/party_shares_selected_wide_2000_2021.csv",
"demo": ROOT/"data/processed/demographics/phase2/demographics_current_2022.csv",
"analysis": ROOT/"data/processed/panels/phase3/analysis_panel_2011_2021.csv",
"turnout_eval": ROOT/"data/processed/models/phase4/turnout_model_comparison_2021.csv",
"party_eval": ROOT/"data/processed/models/phase5/party_support_model_comparison_2021.csv",
"party_methods": ROOT/"data/processed/models/phase5/party_support_selected_methods.csv",
"party_overall": ROOT/"data/processed/models/phase5/party_support_overall_metrics_2021.csv",
"scenario": ROOT/"data/processed/scenarios/phase6/municipality_scenarios_2026.csv",
"method": ROOT/"data/processed/scenarios/phase6/phase6_methodology.csv",
"qc": ROOT/"data/processed/scenarios/phase6/phase6_quality_control.csv",
}

missing = [str(p.relative_to(ROOT)) for p in PATHS.values() if not p.exists()]
if missing:
    st.error("The dashboard cannot start because required processed outputs are missing.")
    st.code("\n".join(missing))
    st.info("Run the Phase 1–6 notebooks first, then refresh this app.")
    st.stop()

@st.cache_data(show_spinner=False)
def load():
    return {k:pd.read_csv(v) for k,v in PATHS.items()}
D=load()
E,P,DEM,A = D["elections"],D["party"],D["demo"],D["analysis"]
TE,PE,PM,PO = D["turnout_eval"],D["party_eval"],D["party_methods"],D["party_overall"]
S,METH,QC = D["scenario"],D["method"],D["qc"]

for df in [E,P,DEM,A,S]:
    if "MuniCode" in df:
        df["Municipality"] = df["MuniCode"].map(MUNICIPALITIES).fillna(df["MuniCode"])

# selected party OTHER where needed
if "OTHER" not in P.columns:
    base = [x for x in PARTIES[:-1] if x in P.columns]
    P["OTHER"]=(100-P[base].fillna(0).sum(axis=1)).clip(lower=0)

# --------------------------- SIDEBAR -------------------------------
st.sidebar.markdown("## EC Electoral Dynamics")
st.sidebar.caption("Eastern Cape · Local Government Elections")
options=(S[["MuniCode","Municipality"]].drop_duplicates()
         .sort_values("Municipality"))
muni=st.sidebar.selectbox("Explore municipality", options["Municipality"])
code=options.loc[options["Municipality"]==muni,"MuniCode"].iloc[0]
st.sidebar.divider()
st.sidebar.markdown("**Evidence layers**")
st.sidebar.caption("Observed elections · demographic context · historical validation · model-based scenarios")
st.sidebar.divider()
st.sidebar.caption("Research prototype · University of Fort Hare DIRISA project")
st.sidebar.info("Future values are scenarios derived from historical models, not known outcomes.")

# --------------------------- HEADER --------------------------------
latest=E[(E.MuniCode==code)&(E.Year==2021)].iloc[0]
sr=S[S.MuniCode==code].iloc[0]

st.markdown(f"""
<div class="hero">
<h1 style="margin:0">Eastern Cape Municipal Electoral Dynamics</h1>
<p style="margin:.4rem 0 0;opacity:.78">
Historical participation, political competition and model-based 2026 scenarios
across Eastern Cape municipalities.
</p>
</div>
""",unsafe_allow_html=True)

st.markdown(f"### {muni}  ·  `{code}`")
k1,k2,k3,k4=st.columns(4)
k1.metric("2021 turnout",f"{latest['Turnout_%']:.1f}%")
k2.metric("2026 turnout scenario",f"{sr['TurnoutScenario_2026']:.1f}%",
          f"{sr['TurnoutScenario_2026']-latest['Turnout_%']:+.1f} pts vs 2021")
k3.metric("2021 effective parties",f"{latest['ENP']:.2f}")
k4.metric("2021 victory margin",f"{latest['Margin_pts']:.1f} pts")
st.caption(
f"Turnout scenario sensitivity: **{sr['TurnoutSensitivityLow_2026']:.1f}%–"
f"{sr['TurnoutSensitivityHigh_2026']:.1f}%** · Historical MAE: "
f"**{sr['HistoricalMAE_pts']:.3f} pts**"
)

tabs=st.tabs(["Overview","History","Participation & context","Model validation",
             "2026 scenarios","Methods & data"])

# --------------------------- OVERVIEW -------------------------------
with tabs[0]:
    st.subheader("Research at a glance")
    st.markdown("""<div class="section-note">
    <b>Research question.</b> What explains differences in electoral participation
    across Eastern Cape municipalities, and what do historical electoral patterns
    suggest about turnout and party support in the 2026 Local Government Elections?
    </div>""",unsafe_allow_html=True)

    byyear=(E.groupby("Year").agg(
        Municipalities=("MuniCode","nunique"),
        MeanTurnout=("Turnout_%","mean"),
        RegisteredVoters=("RegisteredVoters","sum")).reset_index())
    c1,c2=st.columns([1.25,1])
    with c1:
        fig=px.line(byyear,x="Year",y="MeanTurnout",markers=True,
                    labels={"MeanTurnout":"Mean municipal turnout (%)","Year":"Election year"},
                    title="Eastern Cape turnout across local elections")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### Six-phase evidence pipeline")
        st.markdown("""
        **1. Historical elections** — standardised 2000–2021 IEC results
        **2. Demographics** — temporally aligned Census context
        **3. EDA** — turnout, competition and municipality associations
        **4. Turnout validation** — time-aware historical backtesting
        **5. Party support** — category-specific historical backtesting
        **6. 2026 scenarios** — validated methods carried forward
        """)
        st.caption("Historical evidence and future scenarios are kept visually and methodologically separate.")

    st.subheader("2021 municipality comparison")
    latest_all=E[E.Year==2021].sort_values("Turnout_%")
    fig=px.bar(latest_all,x="Turnout_%",y="Municipality",orientation="h",
               labels={"Turnout_%":"Turnout (%)"},
               title="Observed 2021 turnout")
    fig.update_layout(height=760)
    st.plotly_chart(fig,use_container_width=True)

# --------------------------- HISTORY --------------------------------
with tabs[1]:
    st.subheader(f"Observed election history · {muni}")
    h=E[E.MuniCode==code].sort_values("Year")
    ph=P[P.MuniCode==code].sort_values("Year")
    c1,c2=st.columns(2)
    with c1:
        fig=px.line(h,x="Year",y="Turnout_%",markers=True,
                    labels={"Turnout_%":"Turnout (%)"},title="Turnout history")
        fig.update_yaxes(range=[0,100])
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        vals=[x for x in PARTIES if x in ph.columns]
        pl=ph.melt(id_vars="Year",value_vars=vals,var_name="Party category",
                   value_name="PR vote share (%)")
        fig=px.line(pl,x="Year",y="PR vote share (%)",color="Party category",
                    markers=True,title="PR party-share history")
        fig.update_yaxes(range=[0,100])
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("#### Electoral competition")
    c1,c2=st.columns(2)
    with c1:
        fig=px.line(h,x="Year",y="ENP",markers=True,
                    labels={"ENP":"Effective number of parties"},title="Party fragmentation (ENP)")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=px.line(h,x="Year",y="Margin_pts",markers=True,
                    labels={"Margin_pts":"Victory margin (pts)"},title="Victory margin")
        st.plotly_chart(fig,use_container_width=True)
    show=[x for x in ["Year","RegisteredVoters","VotesCast","Turnout_%","ENP","Margin_pts","NumberOfParties"] if x in h]
    st.dataframe(h[show].round(2),hide_index=True,use_container_width=True)
    st.caption("Party support is based on PR ballots. ENP and margin are calculated from the full party distribution.")

# --------------------------- EDA -------------------------------------
with tabs[2]:
    st.subheader("Participation, competition & demographic context")
    st.info("This section describes municipality-level associations. Correlation does not establish causation or individual voter behaviour.")
    nums=A.select_dtypes(include=np.number).columns
    factors=[x for x in ["ENP","Margin_pts","NumberOfParties","Pop","U15","O65","Med",
                         "NoSch","Matric","Higher","Formal","Water","Elec"] if x in nums]
    a,b=st.columns(2)
    year=a.selectbox("Election year",sorted(A.Year.dropna().unique().astype(int)),index=2 if len(A.Year.unique())>2 else 0)
    factor=b.selectbox("Context variable",factors)
    q=A[A.Year==year].dropna(subset=[factor,"Turnout_%"]).copy()
    q["Municipality"]=q.MuniCode.map(MUNICIPALITIES).fillna(q.MuniCode)
    fig=px.scatter(q,x=factor,y="Turnout_%",hover_name="Municipality",
                   trendline="ols" if len(q)>=3 else None,
                   labels={"Turnout_%":"Turnout (%)"},
                   title=f"{factor} and turnout · {year}")
    st.plotly_chart(fig,use_container_width=True)
    corr=q[factor].corr(q["Turnout_%"])
    c1,c2,c3=st.columns(3)
    c1.metric("Municipalities in plot",len(q))
    c2.metric("Pearson correlation","N/A" if pd.isna(corr) else f"{corr:.3f}")
    c3.metric("Election year",year)

    st.markdown(f"#### 2022 demographic context · {muni}")
    dr=DEM[DEM.MuniCode==code]
    display_cols=[x for x in ["Pop","U15","O65","Med","NoSch","Matric","Higher","Formal","Water","Elec"] if x in DEM.columns]
    if len(dr) and display_cols:
        dd=pd.DataFrame({"Variable":display_cols,"Value":[dr.iloc[0][x] for x in display_cols]})
        st.dataframe(dd.round(2),hide_index=True,use_container_width=True)
    else:
        st.caption("No recognised current demographic display fields are available.")

# --------------------------- VALIDATION -------------------------------
with tabs[3]:
    st.subheader("Historical model validation")
    st.markdown("""<div class="section-note">
    Models are compared on historical holdouts. The selected method is the method
    with the lowest historical error—not the method producing a preferred future scenario.
    </div>""",unsafe_allow_html=True)

    st.markdown("### Turnout")
    te=TE.copy()
    if "TestYear" in te: te=te[te.TestYear==2021]
    te=te.sort_values("MAE_pts")
    best=te.iloc[0]
    a,b,c=st.columns(3)
    a.metric("Selected method",best["Model"])
    b.metric("2021 holdout MAE",f"{best['MAE_pts']:.3f} pts")
    c.metric("2021 holdout RMSE",f"{best['RMSE_pts']:.3f} pts")
    fig=px.bar(te,x="MAE_pts",y="Model",orientation="h",
               labels={"MAE_pts":"MAE (percentage points)"},
               title="Turnout model comparison · 2021 holdout")
    st.plotly_chart(fig,use_container_width=True)
    with st.expander("View turnout validation table"):
        st.dataframe(te.round(3),hide_index=True,use_container_width=True)

    st.markdown("### Party support")
    st.caption("Different party categories were allowed to select different historically best-performing methods.")
    if {"Party","Model","MAE_pts"}.issubset(PE.columns):
        fig=px.bar(PE,x="Party",y="MAE_pts",color="Model",barmode="group",
                   labels={"MAE_pts":"MAE (percentage points)"},
                   title="Party-category model comparison · 2021 holdout")
        st.plotly_chart(fig,use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Selected method by category**")
        st.dataframe(PM.round(3),hide_index=True,use_container_width=True)
    with c2:
        st.markdown("**Overall reconstructed composition**")
        st.dataframe(PO.round(3),hide_index=True,use_container_width=True)
    st.caption("Negative R² for some categories indicates weak generalisation. The dashboard does not imply equal predictability across parties.")

# --------------------------- SCENARIO --------------------------------
with tabs[4]:
    st.subheader("2026 model-based scenarios")
    st.warning("Scenario values extend historical patterns; they are not known future results and should be read with the displayed historical-error sensitivity.")

    a,b,c,d=st.columns(4)
    a.metric("2021 turnout",f"{latest['Turnout_%']:.1f}%")
    b.metric("Central 2026 scenario",f"{sr['TurnoutScenario_2026']:.1f}%")
    c.metric("Sensitivity low",f"{sr['TurnoutSensitivityLow_2026']:.1f}%")
    d.metric("Sensitivity high",f"{sr['TurnoutSensitivityHigh_2026']:.1f}%")
    st.caption(f"Method: **{sr['TurnoutMethod']}** · historical MAE **{sr['HistoricalMAE_pts']:.3f} pts**")

    rows=[]
    for p in PARTIES:
        cen=f"{p}_Scenario_2026"
        if cen in S.columns:
            rows.append({"Party category":p,
                         "Scenario share (%)":sr[cen],
                         "Low (%)":sr.get(f"{p}_SensitivityLow_2026",np.nan),
                         "High (%)":sr.get(f"{p}_SensitivityHigh_2026",np.nan),
                         "Method":sr.get(f"{p}_Method","")})
    sh=pd.DataFrame(rows)
    fig=go.Figure(go.Bar(
        x=sh["Party category"],y=sh["Scenario share (%)"],
        error_y=dict(type="data",symmetric=False,
                     array=(sh["High (%)"]-sh["Scenario share (%)"]).values,
                     arrayminus=(sh["Scenario share (%)"]-sh["Low (%)"]).values)))
    fig.update_layout(title=f"{muni} · 2026 PR party-share scenario",
                      xaxis_title="Party category",yaxis_title="Scenario share (%)")
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Error bars are historical-MAE sensitivity bands, not formal confidence intervals.")

    with st.expander("View party scenario values and methods"):
        st.dataframe(sh.round(2),hide_index=True,use_container_width=True)

    st.markdown("### Compare all municipalities")
    choices={"Turnout":"TurnoutScenario_2026"}
    choices.update({f"{p} share":f"{p}_Scenario_2026" for p in PARTIES if f"{p}_Scenario_2026" in S})
    label=st.selectbox("Scenario metric",list(choices))
    metric=choices[label]
    comp=S[["Municipality",metric]].sort_values(metric)
    fig=px.bar(comp,x=metric,y="Municipality",orientation="h",
               labels={metric:"Scenario value (%)"},
               title=f"Municipality comparison · {label}")
    fig.update_layout(height=760)
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("### Scenario composition across municipalities")
    st.caption("This is a descriptive summary of which category has the largest modelled share in each municipal scenario—not a statement of known future winners.")
    if "ScenarioHighestShareCategory_2026" in S:
        cc=S["ScenarioHighestShareCategory_2026"].value_counts().rename_axis("Category").reset_index(name="Municipalities")
        fig=px.bar(cc,x="Category",y="Municipalities",title="Highest-share category under the model scenario")
        st.plotly_chart(fig,use_container_width=True)

# --------------------------- METHODS ---------------------------------
with tabs[5]:
    st.subheader("Methods, quality control & limitations")
    a,b=st.columns([1,1])
    with a:
        st.markdown("### Phase 6 methodology")
        st.dataframe(METH,hide_index=True,use_container_width=True)
    with b:
        st.markdown("### Quality control")
        st.dataframe(QC,hide_index=True,use_container_width=True)
        if "Passed" in QC:
            ok=QC["Passed"].astype(str).str.lower().eq("true").all()
            st.success("All saved Phase 6 QC checks passed.") if ok else st.error("One or more Phase 6 QC checks failed.")

    st.markdown("### Important limitations")
    st.markdown("""
- Historical relationships may not remain stable in 2026.
- Phase 4 showed substantial turnout prediction error on the 2021 holdout.
- Party categories differ materially in historical predictability.
- New parties and structural political changes are difficult to infer from limited election cycles.
- Municipality boundary harmonisation is required for longitudinal comparison.
- Demographic measures describe municipalities and should not be interpreted as individual voter behaviour.
- 2022 demographics are contextual; they were not silently inserted into models that were validated without them.
- MAE-based ranges are historical-error sensitivity bands, not probabilistic confidence intervals.
""")
    st.markdown("### Reproducibility")
    st.markdown("""
The dashboard reads the processed outputs generated by the six analysis notebooks.
It contains **no dummy fallback dataset**. If a required processed file is absent,
the application stops and reports the missing file rather than displaying invented data.
""")
