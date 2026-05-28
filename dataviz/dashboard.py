
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DUCKDB_PATH = "/home/nadege/Downloads/prisoner-dilemma/gold/gold.duckdb"

@st.cache_resource
def get_connection():
    return duckdb.connect(DUCKDB_PATH, read_only=True)

con = get_connection()

# ── Style ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Prisoner Dilemma", page_icon="🎮", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; color: #f0f0f0; }
    h1, h2, h3 { color: #1db954; }
    .metric-card {
        background: #1a1a1a;
        border-left: 3px solid #1db954;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1db954; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎮 Dilemme du Prisonnier Itératif")
st.markdown("**Reproduction du tournoi d'Axelrod (1981) — Pipeline Data Engineering**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prisoners_dilemma.svg/220px-Prisoners_dilemma.svg.png", width=200)
st.sidebar.title("Navigation")
page = st.sidebar.radio("", [
    "🏠 Vue d'ensemble",
    "🏆 Classement",
    "🤝 Coopération",
    "⚔️ Matchs",
    "📈 Evolution temporelle",
    "🔥 Heatmap confrontation",
    "🧠 Comportements avancés",
    "♟️ Equilibre de Nash"
])

st.sidebar.divider()
st.sidebar.markdown("**Stack technique**")
st.sidebar.markdown("🐍 Python + Polars")
st.sidebar.markdown("🤖 Ollama (llama3)")
st.sidebar.markdown("🏗️ dbt + DuckDB")
st.sidebar.markdown("⚡ Prefect")

# ── Chargement données ────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data():
    return {
        "classement": con.execute("SELECT * FROM gold_gold.classement").df(),
        "cooperation": con.execute("SELECT * FROM gold_gold.cooperation_rate").df(),
        "matchs": con.execute("SELECT * FROM gold_gold.match_summary").df(),
        "evolution": con.execute("SELECT * FROM gold_gold.comportement_par_tour").df(),
        "heatmap": con.execute("SELECT * FROM gold_gold.matrice_confrontation").df(),
        "indicateurs": con.execute("SELECT * FROM gold_gold.indicateurs_avances").df(),
        "nash": con.execute("SELECT * FROM gold_gold.nash_equilibre").df(),
    }

data = load_data()

# ── Couleurs par stratégie ────────────────────────────────────────────────────
COLORS = {
    "always_cooperate": "#1db954",
    "always_defect":    "#e74c3c",
    "tit_for_tat":      "#3498db",
    "grim_trigger":     "#f39c12",
    "random":           "#9b59b6",
    "empathique":       "#00d2ff",
    "calculateur":      "#ff6b6b",
}

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Vue d'ensemble":

    df_c = data["classement"]
    df_coop = data["cooperation"]
    df_m = data["matchs"]

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🥇 Stratégie dominante", df_c.iloc[0]["strategy"].replace("_", " ").title())
    col2.metric("📊 Stratégies testées", len(df_c))
    col3.metric("⚔️ Matchs joués", len(df_m))
    col4.metric("🔄 Tours totaux", int(df_c["nb_tours"].sum()))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Classement rapide")
        fig = px.bar(
            df_c.sort_values("score_total"),
            x="score_total",
            y="strategy",
            orientation="h",
            color="strategy",
            color_discrete_map=COLORS,
            title="Score total par stratégie"
        )
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🤝 Coopération vs Trahison")
        fig = px.scatter(
            df_coop,
            x="taux_cooperation",
            y="score_moyen",
            size="score_total",
            color="strategy",
            color_discrete_map=COLORS,
            text="strategy",
            title="Plus de coopération = meilleur score ?"
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### 📖 Contexte")
    st.info("""
    **Le dilemme du prisonnier itératif** modélise une tension universelle :
    faut-il coopérer avec l'autre au risque d'être trahi, ou trahir pour éviter d'être exploité ?

    En 1981, **Robert Axelrod** organisa un tournoi où des programmes s'affrontaient.
    Résultat inattendu : la stratégie la plus simple — **Tit for Tat** (donnant-donnant) — surclassa toutes les autres.

    Ce dashboard reproduit ce tournoi avec des **stratégies codées** et des **agents IA (llama3)**.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Classement":

    df = data["classement"]
    st.subheader("🏆 Classement final du tournoi")

    # Tableau stylé
    st.dataframe(
        df.style.background_gradient(subset=["score_total"], cmap="Greens")
               .format({"score_moyen_par_tour": "{:.2f}"}),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df,
            x="strategy",
            y="score_total",
            color="strategy",
            color_discrete_map=COLORS,
            title="Score total — Classement",
            text="score_total"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df,
            x="strategy",
            y="score_moyen_par_tour",
            color="strategy",
            color_discrete_map=COLORS,
            title="Score moyen par tour",
            text="score_moyen_par_tour"
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — COOPÉRATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Coopération":

    df = data["cooperation"]
    st.subheader("🤝 Analyse de la coopération")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                name=row["strategy"],
                x=[row["strategy"]],
                y=[row["taux_cooperation"]],
                marker_color=COLORS.get(row["strategy"], "#888"),
            ))
        fig.update_layout(
            title="Taux de coopération par stratégie (%)",
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False,
            yaxis_range=[0, 110]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df,
            values="score_total",
            names="strategy",
            color="strategy",
            color_discrete_map=COLORS,
            title="Part du score total par stratégie",
            hole=0.4
        )
        fig.update_layout(
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(
        x=df["taux_cooperation"],
        y=df["score_moyen"],
        mode="markers+text",
        text=df["strategy"],
        textposition="top center",
        marker=dict(
            size=df["score_total"] / 50,
            color=[COLORS.get(s, "#888") for s in df["strategy"]],
            opacity=0.8,
            line=dict(color="white", width=1)
        )
    ))
    fig.update_layout(
        title="Relation entre coopération et performance",
        xaxis_title="Taux de coopération (%)",
        yaxis_title="Score moyen par tour",
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0d0d0d",
        font_color="#f0f0f0"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Observation** : `always_defect` a le meilleur score malgré 0% de coopération — mais uniquement car il exploite les coopérateurs. Dans un tournoi plus long, `tit_for_tat` dominerait.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MATCHS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚔️ Matchs":

    df = data["matchs"]
    st.subheader("⚔️ Résultats des matchs")

    # Comptage victoires
    victoires = df["gagnant"].value_counts().reset_index()
    victoires.columns = ["strategie", "victoires"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            victoires,
            x="strategie",
            y="victoires",
            color="strategie",
            color_discrete_map=COLORS,
            title="Nombre de victoires par stratégie",
            text="victoires"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df,
            x="match",
            y="coop_mutuelle_pct",
            color="gagnant",
            color_discrete_map=COLORS,
            title="% coopération mutuelle par match",
            text="gagnant"
        )
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — EVOLUTION TEMPORELLE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Evolution temporelle":

    df = data["evolution"]
    st.subheader("📈 Evolution du comportement au fil des tours")

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Taux coopération mutuelle",
            "Taux trahison",
            "Gain moyen J1",
            "Gain moyen J2"
        ]
    )

    fig.add_trace(go.Scatter(x=df["tour"], y=df["taux_coop_mutuelle"],
                             mode="lines", name="Coop mutuelle",
                             line=dict(color="#1db954")), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["tour"], y=df["taux_trahison_j1"],
                             mode="lines", name="Trahison J1",
                             line=dict(color="#e74c3c")), row=1, col=2)

    fig.add_trace(go.Scatter(x=df["tour"], y=df["gain_moyen_j1"],
                             mode="lines", name="Gain J1",
                             line=dict(color="#3498db")), row=2, col=1)

    fig.add_trace(go.Scatter(x=df["tour"], y=df["gain_moyen_j2"],
                             mode="lines", name="Gain J2",
                             line=dict(color="#f39c12")), row=2, col=2)

    fig.update_layout(
        height=600,
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0d0d0d",
        font_color="#f0f0f0",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Observation** : Le taux de coopération mutuelle se stabilise après les premiers tours — les stratégies adaptatives trouvent un équilibre.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔥 Heatmap confrontation":

    df = data["heatmap"]
    st.subheader("🔥 Matrice de confrontation — Score moyen")

    df_pivot = df.pivot(index="strategy_a", columns="strategy_b", values="score_moyen")

    fig = px.imshow(
        df_pivot,
        color_continuous_scale="RdYlGn",
        title="Score moyen de chaque stratégie (ligne) contre chaque adversaire (colonne)",
        text_auto=True,
        aspect="auto"
    )
    fig.update_layout(
        paper_bgcolor="#0d0d0d",
        font_color="#f0f0f0",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Lecture** : Vert = score élevé, Rouge = score faible. La diagonale montre qui exploite qui.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — COMPORTEMENTS AVANCÉS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Comportements avancés":

    df = data["indicateurs"]
    st.subheader("🧠 Indicateurs comportementaux avancés")

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.bar(df, x="strategy", y="taux_pardon",
                     color="strategy", color_discrete_map=COLORS,
                     title="Taux de pardon (%)")
        fig.update_layout(plot_bgcolor="#1a1a1a", paper_bgcolor="#0d0d0d",
                          font_color="#f0f0f0", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df, x="strategy", y="trahison_consecutive",
                     color="strategy", color_discrete_map=COLORS,
                     title="Trahison consécutive (%)")
        fig.update_layout(plot_bgcolor="#1a1a1a", paper_bgcolor="#0d0d0d",
                          font_color="#f0f0f0", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = px.bar(df, x="strategy", y="reactivite_trahison",
                     color="strategy", color_discrete_map=COLORS,
                     title="Réactivité à la trahison (%)")
        fig.update_layout(plot_bgcolor="#1a1a1a", paper_bgcolor="#0d0d0d",
                          font_color="#f0f0f0", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    fig = go.Figure()
    categories = ["taux_pardon", "trahison_consecutive", "reactivite_trahison"]
    for _, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["taux_pardon"], row["trahison_consecutive"], row["reactivite_trahison"]],
            theta=["Pardon", "Trahison consécutive", "Réactivité"],
            fill="toself",
            name=row["strategy"],
            line_color=COLORS.get(row["strategy"], "#888")
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1a1a1a",
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        paper_bgcolor="#0d0d0d",
        font_color="#f0f0f0",
        title="Radar — Profil comportemental par stratégie"
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — NASH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "♟️ Equilibre de Nash":

    df = data["nash"]
    st.subheader("♟️ Analyse des équilibres de Nash")

    col1, col2 = st.columns(2)

    with col1:
        type_counts = df["type_equilibre"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.pie(type_counts, values="count", names="type",
                     title="Répartition des types d'équilibre",
                     hole=0.4,
                     color_discrete_sequence=["#1db954", "#e74c3c", "#3498db", "#f39c12", "#9b59b6"])
        fig.update_layout(paper_bgcolor="#0d0d0d", font_color="#f0f0f0")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df,
            x="score_a",
            y="score_b",
            color="type_equilibre",
            symbol="type_equilibre",
            text="strategy_a",
            size_max=15,
            title="Scores par paire — Type d'équilibre",
            color_discrete_sequence=["#1db954", "#e74c3c", "#3498db", "#f39c12", "#9b59b6"]
        )
        fig.add_hline(y=2.5, line_dash="dash", line_color="#888",
                      annotation_text="Seuil coopératif")
        fig.add_vline(x=2.5, line_dash="dash", line_color="#888")
        fig.update_traces(textposition="top center")
        fig.update_layout(
            plot_bgcolor="#1a1a1a",
            paper_bgcolor="#0d0d0d",
            font_color="#f0f0f0"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.dataframe(df, use_container_width=True)

    st.info("""
    💡 **Conclusion d'Axelrod** :
    - Les **équilibres coopératifs** (vert) émergent entre stratégies qui se souviennent du passé
    - L'**équilibre de trahison mutuelle** illustre le dilemme classique
    - **tit_for_tat** maximise les équilibres coopératifs → stratégie optimale à long terme
    """)