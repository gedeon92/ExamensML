import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

# En développement local : API_URL=http://localhost:8000 streamlit run streamlit_app/app.py
API_URL = os.environ.get("API_URL", "https://examensml-api.onrender.com")

st.set_page_config(page_title="Risque d'escalade de conflit", page_icon="🌍")
st.title("🌍 Scoring du risque d'escalade de conflit géopolitique")
st.caption(
    "Saisis les indicateurs d'un pays pour un mois donné : l'API renvoie une "
    "probabilité d'escalade de conflit dans les 6 mois suivants."
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
    col1, col2 = st.columns(2)

    with col1:
        country = st.selectbox("Pays", options=countries or ["France"], index=0)
        region = st.selectbox("Région", options=regions or ["Western Europe"], index=0)
        month = st.date_input("Mois de référence", value=date.today()).strftime("%Y-%m")
        regime_type = st.selectbox("Type de régime", ["Democracy", "Hybrid", "Authoritarian"])
        gdp_growth_pct = st.number_input("Croissance du PIB (%)", value=1.5, step=0.1)
        inflation_rate = st.number_input("Taux d'inflation (%)", value=3.0, step=0.1)
        unemployment_rate = st.number_input("Taux de chômage (%)", value=7.0, step=0.1)
        food_price_index = st.number_input("Indice des prix alimentaires", value=100.0, step=1.0)
        energy_dependency_pct = st.number_input("Dépendance énergétique (%)", value=40.0, step=1.0)
        military_expenditure_pct_gdp = st.number_input("Dépenses militaires (% PIB)", value=2.0, step=0.1)
        arms_imports_index = st.number_input("Indice d'importation d'armes", value=25.0, step=1.0)

    with col2:
        border_disputes_count = st.number_input("Nb de différends frontaliers", value=0, min_value=0, step=1)
        refugee_outflow_thousands = st.number_input("Flux de réfugiés sortants (milliers)", value=10.0, step=1.0)
        sanctions_active = int(st.checkbox("Sanctions internationales actives"))
        media_freedom_score = st.number_input("Score de liberté de la presse (0-100)", value=60.0, step=1.0)
        protest_events_last_3m = st.number_input("Événements de protestation (3 derniers mois)", value=2, min_value=0, step=1)
        rolling_protest_avg_6m = st.number_input("Moyenne mobile des protestations (6 mois)", value=2.0, step=0.1)
        cyber_attack_incidents = st.number_input("Incidents de cyberattaque", value=3, min_value=0, step=1)
        last_conflict_year = st.number_input(
            "Année du dernier conflit connu (0 si aucun)", value=0, min_value=0, step=1
        )
        trade_dependency_rival_pct = st.number_input("Dépendance commerciale à un rival (%)", value=25.0, step=1.0)
        foreign_troops_present = int(st.checkbox("Présence de troupes étrangères"))
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
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as exc:
        st.error(f"Impossible de contacter l'API ({API_URL}) : {exc}")
    else:
        probability = result["probability"]
        risk_level = result["risk_level"]

        st.subheader("Résultat")
        st.metric("Probabilité d'escalade (6 mois)", f"{probability:.1%}")
        st.progress(min(max(probability, 0.0), 1.0))

        if risk_level == "élevé":
            st.error(
                f"⚠️ Risque **élevé** — surveillance rapprochée recommandée pour {country}."
            )
        elif risk_level == "modéré":
            st.warning(
                f"🟠 Risque **modéré** — à surveiller pour {country} dans les prochains mois."
            )
        else:
            st.success(f"🟢 Risque **faible** pour {country} sur la période considérée.")

        st.caption(f"Modèle utilisé : {result['model_name']}")
