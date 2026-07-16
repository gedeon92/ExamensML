"""Feature engineering partagé entre le notebook (Étape 2) et l'API (Étape 5).

Reproduit exactement les transformations appliquées dans ExamenML.ipynb sur les
données brutes, pour qu'un enregistrement envoyé à l'API subisse le même
traitement que les données d'entraînement avant d'entrer dans `model.joblib`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def engineer_features(raw: dict) -> pd.DataFrame:
    """Transforme un enregistrement brut (dict) en une ligne prête pour le pipeline sklearn."""
    row = dict(raw)

    month_date = pd.to_datetime(row.pop("month"), format="%Y-%m")
    row["month_sin"] = np.sin(2 * np.pi * month_date.month / 12)
    row["month_cos"] = np.cos(2 * np.pi * month_date.month / 12)

    last_conflict_year = row.pop("last_conflict_year")
    row["no_prior_conflict_on_record"] = int(last_conflict_year == 0)
    row["years_since_last_conflict"] = (
        np.nan if last_conflict_year == 0 else month_date.year - last_conflict_year
    )

    row["protest_acceleration"] = row["protest_events_last_3m"] - row["rolling_protest_avg_6m"]
    row["economic_pressure_index"] = (
        row["inflation_rate"] + row["unemployment_rate"] + row["food_price_index"] / 10
    )

    return pd.DataFrame([row])
