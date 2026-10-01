"""Eastern Cape Municipal Electoral Dynamics: interactive dashboard.

Run from the repository root:   streamlit run app/app.py

The app only READS the processed outputs written by notebooks 01-06. The
scenario explorer calls the same functions as Notebook 06 (src/models/scenarios.py),
so the dashboard cannot drift from the analysis. Validated evidence is shown in
teal; anything that is an assumption is marked in aloe orange.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import config as C  # noqa: E402
from src.models import scenarios as S  # noqa: E402

st.set_page_config(page_title="Eastern Cape Electoral Dynamics", layout="wide",
                   initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,650&display=swap');
.block-container {{max-width: 1280px; padding-top: 2.2rem;}}
h1, h2, h3 {{font-family: 'Source Serif 4', Georgia, serif; color: {C.INK}; letter-spacing: -0.01em;}}
h1 {{font-size: 2.3rem; line-height: 1.15;}}
.lede {{font-size: 1.08rem; color: #3F5054; max-width: 70ch; line-height: 1.55;}}
.evidence {{border-left: 4px solid {C.TEAL}; background: {C.MIST}; padding: .8rem 1rem; border-radius: 4px; margin: .4rem 0 1rem;}}
.assumption {{border-left: 4px solid {C.ALOE}; background: #FBEDE7; padding: .8rem 1rem; border-radius: 4px; margin: .4rem 0 1rem;}}
.finding {{padding: .2rem 0 .9rem; max-width: 70ch;}}
.finding b {{color: {C.TEAL};}}
.muted {{color: #5C6B6E; font-size: .9rem;}}
[data-testid="stMetricValue"] {{font-family: 'Source Serif 4', Georgia, serif;}}
</style>
""", unsafe_allow_html=True)

PLOT_FONT = dict(family="Segoe UI, Helvetica, Arial, sans-serif", color=C.INK, size=13)
SEQ = [[0, "#F1F5F3"], [0.35, C.TEAL_LIGHT], [0.7, C.TEAL], [1, "#08302E"]]


def style(fig, height=420, legend=True):
    fig.update_layout(font=PLOT_FONT, height=height, margin=dict(l=10, r=10, t=50, b=10),
                      plot_bgcolor="white", paper_bgcolor="white", showlegend=legend,
                      title_font=dict(family="Source Serif 4, Georgia, serif", size=18))
    fig.update_xaxes(gridcolor="#E3E9E8", zeroline=False)
    fig.update_yaxes(gridcolor="#E3E9E8", zeroline=False)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


def note(text, kind="evidence"):
    st.markdown(f'<div class="{kind}">{text}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
FILES = {
    "master": C.DIRS["phase3"] / "master_panel_2000_2021.csv",
    "summary": C.DIRS["phase3"] / "provincial_summary_by_year.csv",
    "assoc": C.DIRS["phase3"] / "turnout_associations_2011_2021.csv",
    "census": C.DIRS["phase2"] / "demographics_current_2022.csv",
    "iec": C.DIRS["phase1"] / "validation_iec_official_municipal.csv",
    "rel": C.DIRS["phase4"] / "turnout_relative_scores.csv",
    "tpred": C.DIRS["phase4"] / "turnout_backtest_predictions.csv",
    "full": C.DIRS["phase4"] / "turnout_full_scores.csv",
    "qc1": C.DIRS["phase1"] / "phase1_quality_control.csv",
    "qc6": C.DIRS["phase6"] / "phase6_quality_control.csv",
    "band": C.DIRS["phase4"] / "turnout_error_band.csv",
    "pmeth": C.DIRS["phase5"] / "party_selected_methods.csv",
    "psum": C.DIRS["phase5"] / "party_backtest_summary.csv",
    "prov": C.DIRS["phase5"] / "provincial_pr_shares_by_year.csv",
    "scen": C.DIRS["phase6"] / "municipality_scenarios_2026.csv",
    "sens": C.DIRS["phase6"] / "swing_sensitivity_2026.csv",
}
missing = [str(p.relative_to(ROOT)) for p in FILES.values() if not p.exists()]
if missing or not C.GEOJSON.exists():
    st.error("The dashboard needs the processed outputs. Run `python run_pipeline.py` from the repository root, then reload.")
    st.code("\n".join(missing + ([] if C.GEOJSON.exists() else [str(C.GEOJSON.relative_to(ROOT))])))
    st.stop()


@st.cache_data(show_spinner=False)
def load():
    d = {k: pd.read_csv(v) for k, v in FILES.items()}
    d["geo"] = json.loads(C.GEOJSON.read_text(encoding="utf-8"))
    return d


D = load()
M, SC, GEO = D["master"], D["scen"], D["geo"]
BAND = float(D["band"].set_index("Quantity").loc["80% of historical absolute errors below (pts)", "Value"])
PARTY_MAE = float(D["psum"].iloc[0]["OverallMAE"])
LEVELS = S.turnout_level_presets(M)
NAMES = dict(sorted(C.MUNICIPALITY_NAMES.items(), key=lambda kv: kv[1]))


@st.cache_data(show_spinner=False)
def map_shapes():
    """Polygon outlines per municipality as lon/lat arrays (None-separated parts).

    Maps are drawn as filled shapes on plain axes, so they need no base map or internet
    connection (Plotly's geo charts download one from a CDN and fail offline)."""
    shapes = {}
    for f in GEO["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        xs, ys, best = [], [], None
        for poly in polys:
            ring = poly[0]
            xs += [pt[0] for pt in ring] + [None]
            ys += [pt[1] for pt in ring] + [None]
            if best is None or len(ring) > len(best):
                best = ring
        cx = sum(pt[0] for pt in best) / len(best)
        cy = sum(pt[1] for pt in best) / len(best)
        shapes[f["id"]] = (xs, ys, cx, cy)
    return shapes


def choropleth(df, col, title, colorscale=SEQ, rng=None, labels=None, discrete=None, height=470):
    from plotly.colors import sample_colorscale
    shapes = map_shapes()
    vals = dict(zip(df["MuniCode"], df[col]))
    fig = go.Figure()
    if discrete:
        for code_, (xs, ys, _, _) in shapes.items():
            v = vals.get(code_)
            colr = discrete.get(v, "#D9DEDD")
            fig.add_scatter(x=xs, y=ys, fill="toself", fillcolor=colr, mode="lines", line=dict(color="white", width=0.8),
                            hoveron="fills", name=f"{C.muni_name(code_)}: {v}", showlegend=False, hoverinfo="name")
        for cat, colr in discrete.items():
            if cat in set(vals.values()):
                fig.add_scatter(x=[None], y=[None], mode="markers", marker=dict(size=12, color=colr, symbol="square"), name=cat)
    else:
        lo, hi = rng if rng else (float(np.nanmin(df[col])), float(np.nanmax(df[col])))
        for code_, (xs, ys, _, _) in shapes.items():
            v = vals.get(code_)
            if v is None or pd.isna(v):
                colr, txt = "#D9DEDD", "no data"
            else:
                colr = sample_colorscale(colorscale, [min(max((v - lo) / (hi - lo), 0), 1)])[0]
                txt = f"{v:.1f}"
            fig.add_scatter(x=xs, y=ys, fill="toself", fillcolor=colr, mode="lines", line=dict(color="white", width=0.8),
                            hoveron="fills", name=f"{C.muni_name(code_)}: {txt}", showlegend=False, hoverinfo="name")
        fig.add_scatter(x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
                        marker=dict(colorscale=colorscale, cmin=lo, cmax=hi, color=[lo], showscale=True,
                                    colorbar=dict(thickness=12, len=0.7, outlinewidth=0)))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1.18)  # ~1/cos(32 deg S)
    fig.update_layout(title=title, hoverlabel=dict(bgcolor="white"))
    fig = style(fig, height)
    fig.update_layout(legend=dict(orientation="h", y=-0.02))
    return fig


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
st.sidebar.markdown("### Eastern Cape Electoral Dynamics")
st.sidebar.caption("Local Government Elections 2000 to 2021, with 2026 scenarios")
PAGES = ["Overview", "1. Participation", "2. Competition", "3. Socioeconomic context", "4. Historical validation",
         "5. 2026 scenarios", "6. Limitations", "Municipality profile", "Methods and QC", "Download the data"]
page = st.sidebar.radio("Go to", PAGES, label_visibility="collapsed")
st.sidebar.divider()
muni = st.sidebar.selectbox("Municipality", list(NAMES.values()),
                            index=list(NAMES.values()).index("Buffalo City"))
code = [k for k, v in NAMES.items() if v == muni][0]
st.sidebar.divider()
st.sidebar.markdown('<span class="muted">Teal panels show validated evidence. Orange panels mark assumptions. '
                    'Values for 2026 are scenarios, not forecasts.</span>', unsafe_allow_html=True)
st.sidebar.caption("University of Fort Hare, DIRISA Student Datathon Challenge 2026")

m21 = M[M["Year"] == 2021]
lvl = M.groupby("Year")["ProvincialLevel_%"].first()

# ----------------------------------------------------------------------------
# Overview
# ----------------------------------------------------------------------------
if page == "Overview":
    st.markdown("# Who turns out in the Eastern Cape, and what could 2026 look like?")
    st.markdown('<p class="lede">Five local elections, 33 municipalities and one consistent map. This dashboard '
                'rebuilds two decades of IEC results, shows what goes with higher or lower turnout, tests whether '
                'turnout and party support could have been predicted before the 2021 election, and turns the validated '
                'patterns into clearly labelled scenarios for 4 November 2026.</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.55, 1])
    with c1:
        metric_opts = {"Turnout (%)": "Turnout_%", "Turnout relative to the province (pts)": "RelativeTurnout_pts",
                       "Effective number of parties": "ENP", "Victory margin (pts)": "Margin_pts",
                       "ANC share (%)": "ANC", "DA share (%)": "DA", "EFF share (%)": "EFF",
                       "Change in turnout since previous election (pts)": "TurnoutChange_pts"}
        a, b = st.columns([1.4, 1])
        label = a.selectbox("Map", list(metric_opts))
        year = b.select_slider("Election", options=C.ELECTION_YEARS, value=2021)
        col = metric_opts[label]
        d = M[M["Year"] == year][["MuniCode", col]]
        if col in ("RelativeTurnout_pts", "TurnoutChange_pts"):
            lim = float(np.nanmax(np.abs(M[col])))
            fig = choropleth(d, col, f"{label}, {year}", colorscale=[[0, C.ALOE], [0.5, "#F7F7F7"], [1, C.TEAL]],
                             rng=[-lim, lim], labels={col: ""})
        else:
            fig = choropleth(d, col, f"{label}, {year}", rng=[M[col].min(), M[col].max()], labels={col: ""})
        show(fig)
        if year == 2000:
            st.caption("Matatiele joined the Eastern Cape in 2006 and has no 2000 value.")
    with c2:
        st.markdown("### Four findings")
        st.markdown(f"""
<div class="finding"><b>Every municipality lost turnout in 2021.</b> All 33 fell, by 4 to 18 points;
the provincial level dropped from {lvl[2016]:.1f}% to {lvl[2021]:.1f}%. This was a province-wide shock, not a local one.</div>
<div class="finding"><b>Within an election, context matters.</b> Older, better-serviced municipalities and closer contests go
with higher turnout. Pooling elections hides this and even reverses some signs.</div>
<div class="finding"><b>Relative position is predictable.</b> Keeping each municipality's 2016 position predicted its 2021
position to within about 2.1 points (r = 0.77), better than ridge regression or random forests.</div>
<div class="finding"><b>The provincial level is not.</b> No method foresaw the 2021 drop: absolute 2021 error was about
8.2 points for every method. So 2026 participation is shown as three explicit assumptions, and Nelson Mandela Bay remains
too close to call.</div>
""", unsafe_allow_html=True)
    note("Data: IEC detailed Local Government Election results 2000 to 2021 (PR ballot), validated against the IEC's "
         "official turnout reports; Stats SA Census 2011 and 2022 municipal indicators. Associations describe "
         "municipalities, not individual voters.")

# ----------------------------------------------------------------------------
# Municipality profile
# ----------------------------------------------------------------------------
elif page == "Municipality profile":
    h = M[M["MuniCode"] == code].sort_values("Year")
    r21 = h[h["Year"] == 2021].iloc[0]
    rank = int(m21.set_index("MuniCode")["Turnout_%"].rank(ascending=False)[code])
    s = SC[SC["MuniCode"] == code].iloc[0]
    leader21 = max(C.PARTIES, key=lambda p: r21[p])
    st.markdown(f"# {muni}")
    st.markdown(f'<p class="lede">{C.DISTRICTS[code]} district, code {code}. '
                f'{int(r21["RegisteredVoters"]):,} registered voters in 2021.</p>', unsafe_allow_html=True)
    k = st.columns(4)
    k[0].metric("2021 turnout", f"{r21['Turnout_%']:.1f}%", f"{r21['TurnoutChange_pts']:+.1f} pts vs 2016")
    k[1].metric("Rank among 33 (2021)", f"{rank}")
    k[2].metric("Relative to province", f"{r21['RelativeTurnout_pts']:+.1f} pts")
    k[3].metric("2021 largest party", leader21, f"lead {r21['Margin_pts']:.1f} pts", delta_color="off")

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_scatter(x=lvl.index, y=lvl.values, name="Provincial level", line=dict(color=C.GREY, dash="dash"))
        fig.add_scatter(x=h["Year"], y=h["Turnout_%"], name=muni, line=dict(color=C.TEAL, width=3), mode="lines+markers")
        fig.update_layout(title="Turnout against the provincial level", yaxis_title="Turnout (%)")
        fig.update_xaxes(tickvals=C.ELECTION_YEARS)
        show(style(fig, 380))
    with c2:
        long = h.melt(id_vars="Year", value_vars=C.PARTIES, var_name="Party", value_name="Share")
        fig = px.area(long, x="Year", y="Share", color="Party", color_discrete_map=C.PARTY_COLORS,
                      title="PR vote share by party", labels={"Share": "PR share (%)"})
        fig.update_xaxes(tickvals=C.ELECTION_YEARS)
        show(style(fig, 380))

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_bar(x=h["Year"], y=h["NumberOfParties"], name="Parties contesting", marker_color="#C9D6D4", yaxis="y2", opacity=.8)
        fig.add_scatter(x=h["Year"], y=h["ENP"], name="Effective number of parties", line=dict(color=C.TEAL, width=3))
        fig.update_layout(title="Political competition", yaxis=dict(title="ENP"),
                          yaxis2=dict(title="Parties", overlaying="y", side="right", showgrid=False))
        fig.update_xaxes(tickvals=C.ELECTION_YEARS)
        show(style(fig, 360))
    with c2:
        cen = D["census"]
        rows = []
        for var, lab in [("U15", "Children under 15 (%)"), ("O65", "Aged 65+ (%)"), ("Matric", "Adults with matric (%)"),
                         ("Higher", "Higher education (%)"), ("Water", "Piped water (%)"), ("Elec", "Electricity (%)"),
                         ("Formal", "Formal dwellings (%)")]:
            rows.append({"Indicator": lab, muni: float(cen.loc[cen["MuniCode"] == code, var].iloc[0]),
                         "Median of 33": float(cen[var].median())})
        dd = pd.DataFrame(rows)
        fig = go.Figure()
        fig.add_bar(y=dd["Indicator"], x=dd["Median of 33"], orientation="h", name="Median of 33", marker_color="#C9D6D4")
        fig.add_bar(y=dd["Indicator"], x=dd[muni], orientation="h", name=muni, marker_color=C.TEAL)
        fig.update_layout(title="Census 2022 profile", barmode="group", xaxis_title="%")
        show(style(fig, 360))

    st.markdown("### 2026 scenarios for this municipality")
    note(f"Turnout = assumed provincial level + this municipality's 2021 relative position ({s['Relative_2026_pts']:+.1f} pts). "
         f"Band: ±{BAND:.1f} pts from historical municipal errors. The provincial level is an assumption.", "assumption")
    c1, c2 = st.columns(2)
    with c1:
        sc = pd.DataFrame({"Scenario": ["Repeat of 2021", "Partial recovery", "Return to 2016"],
                           "Turnout": [s["Turnout_Repeat2021_%"], s["Turnout_PartialRecovery_%"], s["Turnout_Return2016_%"]]})
        fig = go.Figure(go.Bar(x=sc["Scenario"], y=sc["Turnout"], marker_color=[C.ALOE, "#C9A227", C.TEAL_LIGHT],
                               error_y=dict(type="constant", value=BAND, color=C.INK)))
        fig.update_layout(title="Scenario turnout (%)", yaxis_title="Turnout (%)", yaxis_range=[0, 80])
        show(style(fig, 340, legend=False))
    with c2:
        ps = pd.DataFrame({"Party": C.PARTIES, "2021": [s[f"{p}_2021_%"] for p in C.PARTIES],
                           "2026 validated": [s[f"{p}_Validated_%"] for p in C.PARTIES]})
        fig = go.Figure()
        fig.add_bar(x=ps["Party"], y=ps["2021"], name="2021 observed", marker_color="#C9D6D4")
        fig.add_bar(x=ps["Party"], y=ps["2026 validated"], name="2026 status-quo scenario",
                    marker_color=[C.PARTY_COLORS[p] for p in C.PARTIES],
                    error_y=dict(type="constant", value=PARTY_MAE, color=C.INK))
        fig.update_layout(title=f"Party shares: {s['Validated_Status'].lower()}", barmode="group", yaxis_title="PR share (%)")
        show(style(fig, 340))
    prof = h[["Year", "RegisteredVoters", "VotesCast", "Turnout_%", "RelativeTurnout_pts", "ENP", "Margin_pts",
              "NumberOfParties"] + C.PARTIES]
    st.download_button("Download this municipality's history (CSV)", prof.to_csv(index=False).encode(),
                       file_name=f"{code}_history.csv", mime="text/csv")

# ----------------------------------------------------------------------------
# Participation
# ----------------------------------------------------------------------------
elif page == "1. Participation":
    st.markdown("# Participation: a stable plateau, then a province-wide fall")
    st.markdown('<p class="lede">Turnout held at 56 to 58% for four elections, then fell in every one of the 33 '
                'municipalities in 2021. The size of the fall varied, but its direction did not.</p>', unsafe_allow_html=True)
    summ = D["summary"]
    fig = go.Figure()
    for c_, g in M.groupby("MuniCode"):
        fig.add_scatter(x=g["Year"], y=g["Turnout_%"], mode="lines", line=dict(color=C.TEAL_LIGHT, width=1),
                        opacity=.5, showlegend=False, hovertext=C.muni_name(c_), hoverinfo="text+y")
    fig.add_scatter(x=summ["Year"], y=summ["MeanTurnout"], name="Municipal mean", line=dict(color=C.TEAL, width=4))
    fig.add_scatter(x=summ["Year"], y=summ["WeightedTurnout"], name="Registered-voter weighted",
                    line=dict(color=C.ALOE, width=2, dash="dash"))
    fig.update_layout(title="Turnout in every municipality (thin lines) and the provincial average", yaxis_title="Turnout (%)")
    fig.update_xaxes(tickvals=C.ELECTION_YEARS)
    show(style(fig, 430))
    chg = M[M["Year"].isin([2016, 2021])].pivot(index="MuniCode", columns="Year", values="Turnout_%").reset_index()
    chg["Municipality"] = chg["MuniCode"].map(C.muni_name)
    chg["Change"] = chg[2021] - chg[2016]
    chg = chg.sort_values("Change")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        fig = go.Figure()
        for _, r in chg.iterrows():
            fig.add_scatter(x=[r[2016], r[2021]], y=[r["Municipality"]] * 2, mode="lines",
                            line=dict(color="#C9D6D4", width=3), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=chg[2016], y=chg["Municipality"], mode="markers", name="2016", marker=dict(color=C.TEAL, size=8))
        fig.add_scatter(x=chg[2021], y=chg["Municipality"], mode="markers", name="2021", marker=dict(color=C.ALOE, size=8))
        fig.update_layout(title="Every municipality fell, 2016 to 2021", xaxis_title="Turnout (%)")
        show(style(fig, 760))
    with c2:
        show(choropleth(M[M["Year"] == 2021][["MuniCode", "RelativeTurnout_pts"]], "RelativeTurnout_pts",
                        "2021: points above or below the provincial level",
                        colorscale=[[0, C.ALOE], [0.5, "#F7F7F7"], [1, C.TEAL]], rng=[-10, 10],
                        labels={"RelativeTurnout_pts": ""}))
        note(f"Falls ranged from {chg['Change'].max():.1f} to {chg['Change'].min():.1f} points (mean "
             f"{chg['Change'].mean():.1f}). A shock that hits every municipality cannot be explained by differences "
             "between municipalities, so the next pages compare municipalities within each election.")

# ----------------------------------------------------------------------------
# Competition
# ----------------------------------------------------------------------------
elif page == "2. Competition":
    st.markdown("# Competition: more parties, a still-dominant ANC, a few close contests")
    summ = D["summary"]
    c1, c2 = st.columns(2)
    with c1:
        prov = D["prov"].melt(id_vars="Year", var_name="Party", value_name="Share")
        fig = px.bar(prov, x="Year", y="Share", color="Party", color_discrete_map=C.PARTY_COLORS,
                     title="Provincial PR vote share", labels={"Share": "%"})
        fig.update_xaxes(type="category")
        show(style(fig, 400))
    with c2:
        fig = go.Figure()
        fig.add_scatter(x=summ["Year"], y=summ["MeanParties"], name="Parties contesting (mean)", line=dict(color=C.INK, width=3))
        fig.add_scatter(x=summ["Year"], y=summ["MeanENP"], name="Effective number of parties (mean)", line=dict(color=C.TEAL, width=3))
        fig.update_layout(title="More parties, modest fragmentation")
        fig.update_xaxes(tickvals=C.ELECTION_YEARS)
        show(style(fig, 400))
    c1, c2 = st.columns([1, 1])
    with c1:
        yr = st.select_slider("Election", options=C.ELECTION_YEARS, value=2021, key="comp_year")
        show(choropleth(M[M["Year"] == yr][["MuniCode", "Margin_pts"]], "Margin_pts",
                        f"Victory margin, {yr} (pts; lighter = closer)", colorscale=SEQ, rng=[0, 100],
                        labels={"Margin_pts": ""}))
    with c2:
        close = m21[["MuniCode", "Margin_pts", "ENP"] + C.PARTIES].copy()
        close["Municipality"] = close["MuniCode"].map(C.muni_name)
        close["Largest"] = close[C.PARTIES].idxmax(axis=1)
        st.markdown("#### Closest contests, 2021")
        st.dataframe(close.sort_values("Margin_pts")[["Municipality", "Largest", "Margin_pts", "ENP"]].head(8).round(2),
                     hide_index=True, width="stretch")
        note("ENP is computed from every party's votes before small parties are grouped into OTHER. Nelson Mandela Bay "
             "was decided by less than half a point in 2021.")

# ----------------------------------------------------------------------------
# Socioeconomic context
# ----------------------------------------------------------------------------
elif page == "3. Socioeconomic context":
    st.markdown("# Socioeconomic context: two different questions")
    st.markdown('<p class="lede"><b>Across elections</b>, how did participation, competition and living conditions change? '
                '<b>Within an election</b>, why did municipalities differ under the same election-year conditions? '
                'Pooling elections mixes the two, and the 2021 shift can dominate the result.</p>', unsafe_allow_html=True)
    across = (M[M["Year"] >= 2011].groupby("Year")[["Turnout_%", "NumberOfParties", "ENP", "U15", "Matric", "Water", "Elec"]]
              .mean().round(2))
    st.markdown("#### Across elections: provincial means (2016 and 2021 demographics interpolated between censuses)")
    st.dataframe(across, width="stretch")
    nice = {"U15": "Children under 15 (%)", "O65": "Aged 65+ (%)", "Med": "Median age", "Matric": "Adults with matric (%)",
            "Water": "Piped water (%)", "Elec": "Electricity (%)", "Formal": "Formal dwellings (%)",
            "Margin_pts": "Victory margin (pts)", "ENP": "Effective number of parties", "NumberOfParties": "Parties contesting"}
    st.markdown("#### Within an election")
    a, b, c_ = st.columns([1.3, 1, 1])
    var = a.selectbox("Characteristic", list(nice), format_func=nice.get)
    view = b.radio("View", ["Within one election", "Pooled across elections"])
    yr = c_.selectbox("Election", [2011, 2016, 2021], index=1, disabled=view != "Within one election")
    d = M[M["Year"] >= 2011].copy()
    d["Municipality"] = d["MuniCode"].map(C.muni_name)
    d["Election"] = d["Year"].astype(str)
    if view == "Within one election":
        dd = d[d["Year"] == yr]
        fig = px.scatter(dd, x=var, y="Turnout_%", hover_name="Municipality", trendline="ols",
                         color_discrete_sequence=[C.TEAL], labels={var: nice[var], "Turnout_%": "Turnout (%)"},
                         title=f"{nice[var]} and turnout, {yr}: r = {dd[var].corr(dd['Turnout_%']):+.2f}")
    else:
        fig = px.scatter(d, x=var, y="Turnout_%", color="Election", hover_name="Municipality", trendline="ols",
                         trendline_scope="overall", color_discrete_sequence=[C.TEAL, "#4C6A92", C.ALOE],
                         labels={var: nice[var], "Turnout_%": "Turnout (%)"},
                         title=f"Pooled 2011 to 2021: r = {d[var].corr(d['Turnout_%']):+.2f} (mixes change over time with differences between places)")
    show(style(fig, 430))
    at = D["assoc"].copy()
    at = at[at["Variable"].isin(nice)]
    at["Characteristic"] = at["Variable"].map(nice)
    st.markdown("#### All characteristics, 2011 to 2021")
    st.dataframe(at[["Characteristic", "WithinYear_r", "WithinYear_lo", "WithinYear_hi", "Pooled_r", "r_2011", "r_2016", "r_2021", "SignFlip"]]
                 .rename(columns={"WithinYear_r": "Within-election r", "WithinYear_lo": "95% low", "WithinYear_hi": "95% high",
                                  "Pooled_r": "Pooled r", "SignFlip": "Pooled sign differs"}).round(2),
                 hide_index=True, width="stretch")
    note("Within an election, older, better-serviced municipalities and closer contests go with higher turnout. Election "
         "year alone explains 51% of turnout variation (2011 to 2021); municipal characteristics raise this to 63% but overlap "
         "too much to separate. These are municipality-level associations: not causal, and not about individual voters.")

# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
elif page == "4. Historical validation":
    st.markdown("# Historical validation")
    st.markdown('<p class="lede">First, is the data right? Then, with 2021 locked away as a test year, could turnout and '
                'party support have been predicted from earlier elections?</p>', unsafe_allow_html=True)
    st.markdown("### Data: checked against the IEC's official turnout reports")
    iec = D["iec"]
    v = iec.groupby("Year").agg(Municipalities=("MuniCode", "count"),
                                RegisteredVotersMatching=("RegisteredVoters", lambda x: int((x == iec.loc[x.index, "RegisteredVoters_IEC"]).sum())),
                                MeanAbsTurnoutDiff_pts=("TurnoutDiff_pts", lambda x: x.abs().mean())).round(2)
    v.columns = ["Municipalities", "Registered voters equal", "Mean turnout gap (pts)"]
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.dataframe(v, width="stretch")
        st.caption("Small turnout differences arise because the IEC also counts special votes and ward ballots. Province "
                   "totals for 2000 to 2011 also reconcile (Notebook 01).")
    with c2:
        fig = px.scatter(iec.assign(Election=iec["Year"].astype(str)), x="Turnout_%_IEC", y="Turnout_%", color="Election",
                         color_discrete_sequence=[C.TEAL, C.ALOE], title="Reconstructed vs official turnout",
                         labels={"Turnout_%_IEC": "Official IEC turnout (%)", "Turnout_%": "Reconstructed (%)"})
        fig.add_shape(type="line", x0=38, y0=38, x1=70, y1=70, line=dict(color=C.GREY, dash="dash"))
        show(style(fig, 330))

    st.markdown("### Turnout: methods chosen on 2011 and 2016, tested once on 2021")
    rel = D["rel"]
    tbl = rel.pivot_table(index="Model", columns="TestYear", values="MAE")
    tbl["Mean validation (2011, 2016)"] = tbl[[2011, 2016]].mean(axis=1)
    tbl = tbl.sort_values("Mean validation (2011, 2016)").round(2)
    tbl.columns = [f"{c} {'test' if c == 2021 else 'validation'}" if not isinstance(c, str) else c for c in tbl.columns]
    st.dataframe(tbl, width="stretch")
    full = D["full"]
    f21 = full[(full["TestYear"] == 2021) & (full["RelativeModel"] == "Relative persistence") & (full["LevelMethod"] == "Previous level")].iloc[0]
    r21 = rel[(rel["TestYear"] == 2021) & (rel["Model"] == "Relative persistence")].iloc[0]
    two = pd.DataFrame([
        {"Measure": "Absolute turnout error (includes the province-wide 2021 fall)", "MAE (pts)": f21["MAE"],
         "Mean error (pts)": f21["Bias"], "r": f21["r"]},
        {"Measure": "Relative-pattern error (after removing the common election-level shift)", "MAE (pts)": r21["MAE"],
         "Mean error (pts)": r21["Bias"], "r": r21["r"]},
    ]).round(2)
    st.markdown("#### Locked 2021 test: two measures reported separately")
    st.dataframe(two, hide_index=True, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Scatter(x=lvl.index, y=lvl.values, mode="lines+markers+text", text=[f"{x:.1f}" for x in lvl.values],
                                   textposition="top center", line=dict(color=C.TEAL, width=3)))
        fig.update_layout(title="Provincial level: the part no model foresaw", yaxis_title="Mean municipal turnout (%)",
                          yaxis_range=[44, 62])
        fig.update_xaxes(tickvals=C.ELECTION_YEARS)
        show(style(fig, 360, legend=False))
    with c2:
        p = D["tpred"]
        p21 = p[p["Year"] == 2021].copy()
        p21["Municipality"] = p21["MuniCode"].map(C.muni_name)
        fig = px.scatter(p21, x="RelativeTurnout_pts", y="Rel|Relative persistence", hover_name="Municipality",
                         color_discrete_sequence=[C.TEAL],
                         labels={"RelativeTurnout_pts": "Actual 2021 relative turnout (pts)",
                                 "Rel|Relative persistence": "Predicted from 2016 (pts)"},
                         title="Relative municipal pattern: well predicted")
        fig.add_shape(type="line", x0=-11, y0=-11, x1=11, y1=11, line=dict(color=C.GREY, dash="dash"))
        show(style(fig, 360, legend=False))
    note(f"Relative persistence won on the validation folds and was then tested once: absolute 2021 error {f21['MAE']:.2f} points "
         f"(predictions {f21['Bias']:.1f} points too high, the province-wide fall), relative-pattern error {r21['MAE']:.2f} points "
         f"(r = {r21['r']:.2f}). The provincial level was hard to anticipate; municipal differences were stable.")

    st.markdown("### Party support: same locked design")
    ps = D["psum"].copy()
    show_cols = ["Approach", "OverallMAE", "OverallRMSE", "LeaderMatches"] + [f"MAE_{p}" for p in C.PARTIES]
    st.dataframe(ps[show_cols].round(2), hide_index=True, width="stretch")
    with st.expander("Selected method by party, and why"):
        st.dataframe(D["pmeth"][["Party", "SelectedMethod", "MeanValidationMAE", "Reason"]], hide_index=True, width="stretch")
    note("The validated composite beats the no-change baseline overall (2.69 against 2.93 points). Identifying the largest "
         "party is an easy test here: the baseline also gets 33 of 33. The earlier prototype chose methods using 2021 itself, "
         "so its 2.50 and 32 of 33 are not valid test results and are shown only for comparison.")

# ----------------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------------
elif page == "5. 2026 scenarios":
    st.markdown("# 2026 scenarios")
    note("Scenarios combine validated municipal patterns with assumptions you choose. They show how outcomes respond to "
         "those assumptions; they are not predictions and do not establish causes.", "assumption")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Turnout assumption")
        options = list(LEVELS) + ["Custom level"]
        choice = st.radio("Provincial turnout level", options, index=1)
        level = st.slider("Custom provincial level (%)", 40.0, 65.0, 52.0, 0.5) if choice == "Custom level" else LEVELS[choice]
        st.caption(f"Observed levels: 2016 {lvl[2016]:.1f}%, 2021 {lvl[2021]:.1f}%.")
    with c2:
        st.markdown("#### Party assumption")
        base_choice = st.radio("Starting composition", ["Validated status quo", "Trend continues (not validated)"])
        cols = st.columns(4)
        swings = {p: cols[i].slider(f"{p} swing", -10.0, 10.0, 0.0, 0.5) for i, p in enumerate(["ANC", "DA", "EFF", "OTHER"])}
        st.caption("Uniform percentage-point swings applied in every municipality, then rescaled to 100%.")

    rel = SC[["MuniCode", "Relative_2026_pts"]].rename(columns={"Relative_2026_pts": "RelativeTurnout_2026"})
    reg = SC.set_index("MuniCode")["RegisteredVoters"]
    turn = S.turnout_scenario(rel, level, BAND, registered=reg)
    key = "Validated" if base_choice.startswith("Validated") else "Trend"
    base = SC[["MuniCode"] + [f"{p}_{key}_%" for p in C.PARTIES]].rename(columns={f"{p}_{key}_%": p for p in C.PARTIES})
    shares = S.apply_swing(base, swings)
    lead = S.leaders(shares, 2 * PARTY_MAE)

    k = st.columns(4)
    k[0].metric("Mean municipal turnout", f"{turn['Turnout_%'].mean():.1f}%")
    k[1].metric("Expected votes cast", f"{turn['ExpectedVotesCast'].sum() / 1e6:.2f} m")
    k[2].metric("Municipalities, ANC largest", int((lead["Leader"] == "ANC").sum()))
    k[3].metric("Too close to call", int(lead["TooCloseToCall"].sum()))
    st.caption(f"Registered voters: {SC['RegistrationBasis'].iloc[0]}.")

    c1, c2 = st.columns(2)
    with c1:
        show(choropleth(turn, "Turnout_%", "Scenario turnout (%)", rng=[35, 70], labels={"Turnout_%": ""}))
    with c2:
        lead["Map"] = np.where(lead["TooCloseToCall"], "Too close to call", lead["Leader"] + " largest")
        cmap = {f"{p} largest": C.PARTY_COLORS[p] for p in C.PARTIES}
        cmap["Too close to call"] = "#F2C14E"
        show(choropleth(lead, "Map", "Largest party under this scenario", discrete=cmap))

    out = turn.merge(shares, on="MuniCode").merge(lead[["MuniCode", "Leader", "RunnerUp", "Gap_pts", "Status"]], on="MuniCode")
    out.insert(1, "Municipality", out["MuniCode"].map(C.muni_name))
    st.dataframe(out.drop(columns=["AssumedLevel_%"]).round(2).sort_values("Gap_pts"), hide_index=True,
                 width="stretch")
    st.download_button("Download this scenario (CSV)", out.to_csv(index=False).encode(), "scenario_2026_custom.csv", "text/csv")

    sens = D["sens"]
    fig = go.Figure()
    fig.add_scatter(x=sens["ANC_to_DA_swing_pts"], y=sens["DA_leads"], name="DA largest",
                    line=dict(color=C.PARTY_COLORS["DA"], width=3))
    fig.add_scatter(x=sens["ANC_to_DA_swing_pts"], y=sens["TooClose"], name="Too close to call",
                    line=dict(color=C.ALOE, dash="dash"))
    fig.update_layout(title="Municipalities changing hands as votes swing from ANC to DA (status-quo start)",
                      xaxis_title="Uniform swing ANC to DA (pts)", yaxis_title="Municipalities")
    show(style(fig, 360))
    st.caption("Not modelled: parties formed after 2021, coalitions, candidates, campaigns and the 2024 national election.")

# ----------------------------------------------------------------------------
# Downloads
# ----------------------------------------------------------------------------
elif page == "Download the data":
    st.markdown("# Download the data")
    st.markdown('<p class="lede">Every number in this dashboard comes from these files, produced by the six notebooks '
                'from the raw IEC and Stats SA inputs.</p>', unsafe_allow_html=True)
    downloads = [
        ("Municipality-election panel, 2000 to 2021", C.DIRS["phase1"] / "municipality_election_panel_2000_2021.csv"),
        ("Party vote shares, all parties (long)", C.DIRS["phase1"] / "party_shares_long_2000_2021.csv"),
        ("Master analytical panel", C.DIRS["phase3"] / "master_panel_2000_2021.csv"),
        ("Turnout associations (within-election)", C.DIRS["phase3"] / "turnout_associations_2011_2021.csv"),
        ("Turnout backtest scores", C.DIRS["phase4"] / "turnout_relative_scores.csv"),
        ("Party backtest summary", C.DIRS["phase5"] / "party_backtest_summary.csv"),
        ("2026 municipal scenarios", C.DIRS["phase6"] / "municipality_scenarios_2026.csv"),
        ("Municipality crosswalk", C.DIRS["phase1"] / "municipality_crosswalk.csv"),
    ]
    for label, path in downloads:
        a, b = st.columns([3, 1])
        a.markdown(f"**{label}**  \n`{path.relative_to(ROOT).as_posix()}`")
        b.download_button("Download", path.read_bytes(), file_name=path.name, mime="text/csv", key=str(path))
    a, b = st.columns([3, 1])
    a.markdown(f"**Map of the 33 municipalities (GeoJSON)**  \n`{C.GEOJSON.relative_to(ROOT).as_posix()}`")
    b.download_button("Download", C.GEOJSON.read_bytes(), file_name=C.GEOJSON.name, mime="application/geo+json")
    st.markdown("### Data dictionary")
    st.dataframe(pd.read_csv(ROOT / "docs" / "data_dictionary.csv"), hide_index=True, width="stretch")

# ----------------------------------------------------------------------------
# Methods
# ----------------------------------------------------------------------------
elif page == "6. Limitations":
    st.markdown("# Limitations")
    st.markdown("""
| Limitation | What it means | How it is handled |
|---|---|---|
| Five elections, 33 municipalities | Few training transitions, limited statistical power | Simple models, baselines, time-ordered validation |
| Boundary changes | Harmonised municipalities are comparable, not identical | Explicit crosswalk; same crosswalk builds the map |
| 2021 held during COVID-19 | Province-wide shock no model could foresee | Level treated as an assumption; relative pattern modelled |
| Ecological data | Associations describe places, not voters; not causal | Careful wording throughout |
| Overlapping characteristics | Separate effects of age, services, competition not separable | Joint interpretation; fixed-effects model |
| Census in 2011 and 2022 only | 2016/2021 values interpolated | Interpolated values used only for description, never for backtests |
| Census file provenance | Upstream tables not recorded in the repository | Flagged; no headline result depends on it |
| No gender or voter-age data province-wide | Gender and youth questions not answerable | Registration hook ready for a 2026 IEC extract |
| New parties and post-2021 events | Not learnable from history | Scenarios with explicit swing levers |
| Error bands | Empirical error scales | Never presented as confidence intervals |
""")

else:
    st.markdown("# Methods and quality control")
    st.markdown("""
**Research question.** What explains differences in electoral participation across Eastern Cape municipalities, and
what do historical electoral patterns suggest about turnout and party support in the 2026 Local Government Elections?

**Pipeline.** Six notebooks, run in order: historical elections, demographics, master panel and analysis, turnout model,
party-support model, 2026 scenarios. Shared logic lives in `src/`; `python run_pipeline.py` rebuilds everything.

**Key choices.**
- PR ballot only, so party support is comparable across elections.
- Registered voters and spoilt ballots counted once per voting district.
- Municipalities harmonised to 33 present-day units with an explicit crosswalk; the same crosswalk builds the map.
- Effective number of parties computed before small parties are grouped.
- Associations analysed within elections, because a province-wide shock in 2021 distorts pooled correlations.
- Rolling-origin validation: methods chosen on 2011 and 2016, tested once on 2021. No random splits.
- Census values used in models only if published before the election (Census 2011 for 2016 and 2021).
- Turnout split into a provincial level (assumption) and relative position (modelled).
""")
    st.markdown("### Sources")
    st.markdown("""
- Electoral Commission of South Africa (IEC): municipal election results downloads, results.elections.org.za
- IEC voter turnout reports for 2000 to 2021 (independent validation)
- IEC voter registration statistics, elections.org.za (2026 snapshot: pipeline ready, data still to be added)
- Statistics South Africa: Census 2011 and Census 2022 municipal indicators
- Municipal Demarcation Board 2011 boundaries, via github.com/datawizzards/zadmaps
""")
    st.markdown("### Quality-control gates (all must pass for the pipeline to complete)")
    c1, c2 = st.columns(2)
    c1.markdown("**Phase 1: election data**"); c1.dataframe(D["qc1"], hide_index=True, width="stretch")
    c2.markdown("**Phase 6: scenarios**"); c2.dataframe(D["qc6"], hide_index=True, width="stretch")
    st.caption("Full documentation: README.md and docs/ in the repository.")
