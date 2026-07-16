from typing import Literal

from pydantic import BaseModel, Field


class CountryRiskInput(BaseModel):
    country: str = Field(..., examples=["France"])
    region: str = Field(..., examples=["Western Europe"])
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", examples=["2025-06"])
    gdp_growth_pct: float = Field(..., examples=[1.2])
    inflation_rate: float = Field(..., examples=[3.5])
    unemployment_rate: float = Field(..., examples=[7.8])
    food_price_index: float = Field(..., examples=[110.0])
    energy_dependency_pct: float = Field(..., examples=[40.0])
    military_expenditure_pct_gdp: float = Field(..., examples=[2.1])
    arms_imports_index: float = Field(..., examples=[30.0])
    border_disputes_count: int = Field(..., ge=0, examples=[0])
    refugee_outflow_thousands: float = Field(..., ge=0, examples=[10.0])
    sanctions_active: Literal[0, 1] = Field(..., examples=[0])
    media_freedom_score: float = Field(..., examples=[70.0])
    protest_events_last_3m: int = Field(..., ge=0, examples=[2])
    cyber_attack_incidents: int = Field(..., ge=0, examples=[3])
    last_conflict_year: int = Field(
        ..., examples=[0], description="0 si aucun conflit connu recensé"
    )
    trade_dependency_rival_pct: float = Field(..., examples=[25.0])
    foreign_troops_present: Literal[0, 1] = Field(..., examples=[0])
    regime_type: Literal["Democracy", "Hybrid", "Authoritarian"] = Field(..., examples=["Democracy"])
    social_media_sentiment: float = Field(..., ge=-1, le=1, examples=[0.0])
    rolling_protest_avg_6m: float = Field(..., ge=0, examples=[2.0])


class PredictionResponse(BaseModel):
    prediction: Literal[0, 1]
    probability: float
    risk_level: Literal["faible", "modéré", "élevé"]
    model_name: str
