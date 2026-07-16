import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

# En développement local : API_URL=http://localhost:8000 streamlit run streamlit_app/app.py
API_URL = os.environ.get("API_URL", "https://examensml-api.onrender.com")

st.set_page_config(
    page_title="Scoring — Risque d'escalade de conflit",
    page_icon="🌍",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Style : palette cohérente avec le support de soutenance (navy + teal signal)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      :root {
        --good: #4caf7d;
        --warning: #d9a441;
        --critical: #d16552;
        --accent: #4fb3c9;
      }

      /* Titre + sous-titre */
      .hero-eyebrow {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
        text-transform: uppercase; color: var(--accent); margin-bottom: 0.3rem;
      }
      .hero-title { font-size: 1.9rem; font-weight: 800; margin: 0 0 0.3rem; }
      .hero-subtitle { color: #8b95ab; font-size: 0.98rem; max-width: 60ch; margin-bottom: 1.6rem; }

      /* Carte du formulaire */
      div[data-testid="stForm"] {
        background: #121a2b;
        border: 1px solid #243050;
        border-radius: 14px;
        padding: 1.6rem 1.6rem 1.2rem;
      }

      /* Onglets */
      .stTabs [data-baseweb="tab-list"] { gap: 0.3rem; }
      .stTabs [data-baseweb="tab"] {
        background: #0a0f1a; border-radius: 8px 8px 0 0; padding: 0.5rem 1rem;
        font-weight: 600; font-size: 0.85rem;
      }

      /* Bouton de soumission */
      div[data-testid="stFormSubmitButton"] button {
        background: var(--accent); color: #06131a; font-weight: 700;
        border: none; border-radius: 10px; padding: 0.6rem 1.4rem; width: 100%;
        transition: filter 0.15s ease;
      }
      div[data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.12); }

      /* Carte résultat */
      .result-card {
        background: #121a2b; border: 1px solid #243050; border-radius: 14px;
        padding: 1.6rem; margin-top: 1.4rem;
        animation: fadein 0.5s ease;
      }
      @keyframes fadein { from { opacity:0; transform: translateY(8px);} to {opacity:1; transform:none;} }

      .risk-badge {
        display:inline-block; padding: 0.3rem 0.9rem; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; margin: 0.4rem auto 0; text-align:center;
      }
      .risk-badge.faible { background: rgba(76,175,125,0.16); color: var(--good); }
      .risk-badge.modéré { background: rgba(217,164,65,0.16); color: var(--warning); }
      .risk-badge.élevé { background: rgba(209,101,82,0.16); color: var(--critical); }
      .risk-center { text-align: center; }
      .risk-explain { color:#8b95ab; font-size:0.88rem; text-align:center; margin-top:0.6rem; max-width:52ch; margin-left:auto; margin-right:auto; }

      /* Jauge circulaire (façon dashboard) */
      .gauge-wrap { display:flex; justify-content:center; margin: 0.4rem 0 0.8rem; }
      .gauge {
        position: relative; width: 176px; height: 176px; border-radius: 50%;
        display:flex; align-items:center; justify-content:center;
      }
      .gauge::before {
        content:""; position:absolute; inset: 14px; border-radius:50%; background:#121a2b;
      }
      .gauge-value { position:relative; z-index:1; text-align:center; }
      .gauge-value .pct { font-size: 2rem; font-weight: 800; }
      .gauge-value .label { font-size:0.78rem; color:#8b95ab; margin-top:0.15rem; }

      /* Barre latérale */
      section[data-testid="stSidebar"] { background:#0a0f1a; border-right:1px solid #1b2438; }
      .side-brand { text-align:center; padding: 0.4rem 0 1.2rem; }
      .side-brand .side-icon {
        width:52px; height:52px; margin:0 auto 0.6rem; border-radius:14px;
        background: linear-gradient(135deg, var(--accent), #2a6f82);
        display:flex; align-items:center; justify-content:center; font-size:1.5rem;
      }
      .side-brand .side-title { font-weight:800; font-size:1rem; }
      .side-brand .side-subtitle { color:#8b95ab; font-size:0.78rem; margin-top:0.2rem; }
      .side-card {
        background:#121a2b; border:1px solid #243050; border-radius:12px;
        padding: 0.9rem 1rem; margin-bottom: 1rem;
      }
      .side-card-title { font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#8b95ab; margin-bottom:0.6rem; }
      .legend-row { display:flex; align-items:center; gap:0.5rem; font-size:0.86rem; padding:0.2rem 0; }
      .legend-row .dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
      .legend-row .dot.good { background: var(--good); }
      .legend-row .dot.warning { background: var(--warning); }
      .legend-row .dot.critical { background: var(--critical); }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">
          <div class="side-icon">🌍</div>
          <div class="side-title">Scoring Conflits</div>
          <div class="side-subtitle">Examen MLOps · Random Forest</div>
        </div>
        <div class="side-card">
          <div class="side-card-title">Légende du risque</div>
          <div class="legend-row"><span class="dot good"></span> Faible</div>
          <div class="legend-row"><span class="dot warning"></span> Modéré</div>
          <div class="legend-row"><span class="dot critical"></span> Élevé</div>
        </div>
        <div class="side-card">
          <div class="side-card-title">À propos</div>
          <div style="color:#8b95ab; font-size:0.84rem;">
            Estime la probabilité d'escalade d'un conflit géopolitique dans les 6 mois,
            à partir d'indicateurs économiques, sécuritaires et sociétaux.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="hero-eyebrow">Examen MLOps · Random Forest</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">🌍 Risque d\'escalade de conflit géopolitique</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Remplis les indicateurs d\'un pays pour un mois donné : '
    "le modèle estime la probabilité d'escalade dans les 6 mois qui suivent.</div>",
    unsafe_allow_html=True,
)


@st.cache_data
def load_reference_lists():
    df = pd.read_csv("geopolitical_conflict_risk_dataset.csv")
    return sorted(df["country"].unique()), sorted(df["region"].unique())


try:
    countries, regions = load_reference_lists()
except FileNotFoundError:
    countries, regions = [], []

with st.form("risk_form"):
    tab_contexte, tab_eco, tab_securite, tab_societe = st.tabs(
        ["🌍 Contexte", "📈 Économie", "🛡️ Sécurité", "📢 Société"]
    )

    with tab_contexte:
        country = st.selectbox("Pays", options=countries or ["France"], index=0)
        region = st.selectbox("Région", options=regions or ["Western Europe"], index=0)
        month = st.date_input("Mois de référence", value=date.today()).strftime("%Y-%m")
        regime_labels = {"Democracy": "Démocratie", "Hybrid": "Hybride", "Authoritarian": "Autoritaire"}
        regime_type = st.selectbox(
            "Type de régime",
            options=list(regime_labels.keys()),
            format_func=lambda v: regime_labels[v],
        )
        last_conflict_year = st.number_input(
            "Année du dernier conflit connu (0 si aucun)", value=0, min_value=0, step=1
        )
        foreign_troops_present = int(st.checkbox("Présence de troupes étrangères"))

    with tab_eco:
        gdp_growth_pct = st.number_input("Croissance du PIB (%)", value=1.5, step=0.1)
        inflation_rate = st.number_input("Taux d'inflation (%)", value=3.0, step=0.1)
        unemployment_rate = st.number_input("Taux de chômage (%)", value=7.0, step=0.1)
        food_price_index = st.number_input("Indice des prix alimentaires", value=100.0, step=1.0)
        energy_dependency_pct = st.number_input("Dépendance énergétique (%)", value=40.0, step=1.0)
        trade_dependency_rival_pct = st.number_input("Dépendance commerciale à un rival (%)", value=25.0, step=1.0)

    with tab_securite:
        military_expenditure_pct_gdp = st.number_input("Dépenses militaires (% PIB)", value=2.0, step=0.1)
        arms_imports_index = st.number_input("Indice d'importation d'armes", value=25.0, step=1.0)
        border_disputes_count = st.number_input("Nb de différends frontaliers", value=0, min_value=0, step=1)
        sanctions_active = int(st.checkbox("Sanctions internationales actives"))
        cyber_attack_incidents = st.number_input("Incidents de cyberattaque", value=3, min_value=0, step=1)
        refugee_outflow_thousands = st.number_input("Flux de réfugiés sortants (milliers)", value=10.0, step=1.0)

    with tab_societe:
        media_freedom_score = st.number_input("Score de liberté de la presse (0-100)", value=60.0, step=1.0)
        protest_events_last_3m = st.number_input("Événements de protestation (3 derniers mois)", value=2, min_value=0, step=1)
        rolling_protest_avg_6m = st.number_input("Moyenne mobile des protestations (6 mois)", value=2.0, step=0.1)
        social_media_sentiment = st.slider("Sentiment sur les réseaux sociaux", -1.0, 1.0, 0.0, 0.05)

    submitted = st.form_submit_button("Évaluer le risque")

if submitted:
    payload = {
        "country": country,
        "region": region,
        "month": month,
        "gdp_growth_pct": gdp_growth_pct,
        "inflation_rate": inflation_rate,
        "unemployment_rate": unemployment_rate,
        "food_price_index": food_price_index,
        "energy_dependency_pct": energy_dependency_pct,
        "military_expenditure_pct_gdp": military_expenditure_pct_gdp,
        "arms_imports_index": arms_imports_index,
        "border_disputes_count": border_disputes_count,
        "refugee_outflow_thousands": refugee_outflow_thousands,
        "sanctions_active": sanctions_active,
        "media_freedom_score": media_freedom_score,
        "protest_events_last_3m": protest_events_last_3m,
        "cyber_attack_incidents": cyber_attack_incidents,
        "last_conflict_year": last_conflict_year,
        "trade_dependency_rival_pct": trade_dependency_rival_pct,
        "foreign_troops_present": foreign_troops_present,
        "regime_type": regime_type,
        "social_media_sentiment": social_media_sentiment,
        "rolling_protest_avg_6m": rolling_protest_avg_6m,
    }

    try:
        with st.spinner("Analyse en cours..."):
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
    except requests.exceptions.RequestException as exc:
        st.error(
            "Impossible de contacter l'API de scoring. Vérifie que le service est démarré, "
            "puis réessaie."
        )
        with st.expander("Détails techniques"):
            st.code(f"URL : {API_URL}\n{exc}")
    else:
        probability = result["probability"]
        risk_level = result["risk_level"]
        pct = probability * 100

        explanations = {
            "faible": "Les indicateurs saisis ne montrent pas de signal d'alerte marqué pour ce pays sur la période.",
            "modéré": "Certains indicateurs (contestation, tensions économiques ou sécuritaires) méritent une surveillance.",
            "élevé": "Plusieurs signaux convergent vers un risque d'escalade — une vigilance renforcée est recommandée.",
        }
        ring_colors = {"faible": "var(--good)", "modéré": "var(--warning)", "élevé": "var(--critical)"}

        st.markdown(
            f"""
            <div class="result-card">
              <div class="risk-center" style="font-size:0.85rem; color:#8b95ab;">Probabilité d'escalade — 6 mois</div>
              <div class="gauge-wrap">
                <div class="gauge" style="background: conic-gradient({ring_colors[risk_level]} {pct}%, #1b2438 0);">
                  <div class="gauge-value">
                    <div class="pct">{pct:.1f}%</div>
                    <div class="label">Risque {risk_level}</div>
                  </div>
                </div>
              </div>
              <div class="risk-center"><span class="risk-badge {risk_level}">
                {"🟢" if risk_level == "faible" else "🟠" if risk_level == "modéré" else "🔴"} Risque {risk_level}
              </span></div>
              <div class="risk-explain">{explanations[risk_level]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"Pays évalué : {country} · Modèle : {result['model_name']}")
