# Examen MLOps — Scoring du risque d'escalade de conflit géopolitique

Projet réalisé pour l'examen "MLOps et déploiement" : cycle complet de la préparation des
données au déploiement d'une API de scoring, avec suivi MLflow, interface Streamlit et
analyse de data drift.

## Structure

- `ExamenML.ipynb` — Étapes 1 à 4 : MLflow, préparation des données, score métier,
  entraînement/comparaison des modèles (Logistic Regression, Random Forest, XGBoost),
  interprétabilité (SHAP, LIME). Produit `model.joblib`.
- `api/` — Étape 5 : API FastAPI de scoring (`main.py`, `schemas.py`,
  `feature_engineering.py`).
- `tests/` — tests de l'API (pytest).
- `streamlit_app/` — Étape 6 : interface utilisateur qui appelle l'API.
- `drift_analysis.ipynb` — Étape 7 : indicateurs de data drift.
- `.github/workflows/ci-cd.yml` — tests automatiques + déploiement continu.
- `Dockerfile` — image de l'API pour un déploiement cloud (Render, Fly.io, AWS, GCP...).

## Lancer le projet en local

```bash
pip install -r requirements-dev.txt

# 1) Notebook : régénère model.joblib et le tracking MLflow
jupyter nbconvert --to notebook --execute --inplace ExamenML.ipynb

# 2) Visualiser MLflow
mlflow ui --backend-store-uri sqlite:///mlflow.db

# 3) Lancer l'API
uvicorn api.main:app --reload

# 4) Tests de l'API
pytest tests/ -v

# 5) Interface Streamlit
streamlit run streamlit_app/app.py
```

## Déploiement

L'API est conteneurisée (`Dockerfile`) et peut être déployée sur n'importe quel service
acceptant une image Docker (Render, Fly.io, AWS App Runner, GCP Cloud Run...). Le workflow
`.github/workflows/ci-cd.yml` lance les tests à chaque push/PR, puis déclenche un
déploiement continu via un webhook (`RENDER_DEPLOY_HOOK_URL`, à configurer comme secret
du repo une fois le service cloud créé).
