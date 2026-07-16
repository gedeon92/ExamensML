import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def sample_payload() -> dict:
    return {
        "country": "France",
        "region": "Western Europe",
        "month": "2025-06",
        "gdp_growth_pct": 1.2,
        "inflation_rate": 3.5,
        "unemployment_rate": 7.8,
        "food_price_index": 110.0,
        "energy_dependency_pct": 40.0,
        "military_expenditure_pct_gdp": 2.1,
        "arms_imports_index": 30.0,
        "border_disputes_count": 0,
        "refugee_outflow_thousands": 10.0,
        "sanctions_active": 0,
        "media_freedom_score": 70.0,
        "protest_events_last_3m": 2,
        "cyber_attack_incidents": 3,
        "last_conflict_year": 0,
        "trade_dependency_rival_pct": 25.0,
        "foreign_troops_present": 0,
        "regime_type": "Democracy",
        "social_media_sentiment": 0.0,
        "rolling_protest_avg_6m": 2.0,
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_returns_valid_response(client):
    response = client.post("/predict", json=sample_payload())
    assert response.status_code == 200

    body = response.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["probability"] <= 1.0
    assert body["risk_level"] in ("faible", "modéré", "élevé")


def test_predict_rejects_invalid_month_format(client):
    payload = sample_payload()
    payload["month"] = "not-a-month"
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_rejects_invalid_regime_type(client):
    payload = sample_payload()
    payload["regime_type"] = "Anarchy"
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
