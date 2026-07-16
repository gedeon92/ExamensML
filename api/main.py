from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .feature_engineering import engineer_features
from .schemas import CountryRiskInput, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parent.parent / "model.joblib"
MODEL_NAME = "random_forest"

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Modèle introuvable à {MODEL_PATH}. Exécute d'abord ExamenML.ipynb (Étape 4) "
            "pour générer model.joblib."
        )
    model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(
    title="API de scoring — risque d'escalade de conflit géopolitique",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: CountryRiskInput) -> PredictionResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé.")

    try:
        features = engineer_features(payload.model_dump())
        probability = float(model.predict_proba(features)[0, 1])
    except Exception as exc:  # noqa: BLE001 — on renvoie l'erreur au client plutôt qu'un 500 opaque
        raise HTTPException(status_code=422, detail=f"Erreur de traitement des features : {exc}") from exc

    prediction = int(probability >= 0.5)
    if probability < 0.3:
        risk_level = "faible"
    elif probability < 0.6:
        risk_level = "modéré"
    else:
        risk_level = "élevé"

    return PredictionResponse(
        prediction=prediction,
        probability=probability,
        risk_level=risk_level,
        model_name=MODEL_NAME,
    )
