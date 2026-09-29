"""Serve the portable logistic-regression model without native ML extensions."""

import json
import math
from functools import lru_cache
from pathlib import Path

from schemas import PatientInput, PredictionResponse

MODEL_PATH = Path(__file__).parent / "model" / "readmission_logistic_model.json"


@lru_cache(maxsize=1)
def get_model():
    """Load the portable model once without importing native ML extensions."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No portable model found at {MODEL_PATH}. "
            "Run export_model.py in an environment that can load the trained model."
        )
    with MODEL_PATH.open(encoding="utf-8") as model_file:
        model = json.load(model_file)

    numeric_count = len(model["numeric_features"])
    category_count = sum(len(categories) for categories in model["categories"])
    if (
        len(model["numeric_mean"]) != numeric_count
        or len(model["numeric_scale"]) != numeric_count
        or len(model["categorical_features"]) != len(model["categories"])
        or len(model["coefficients"]) != numeric_count + category_count
        or any(scale <= 0 for scale in model["numeric_scale"])
    ):
        raise ValueError(f"Invalid portable model artifact: {MODEL_PATH}")
    return model


def _predict_probability(patient: dict, model: dict) -> float:
    coefficients = model["coefficients"]
    coefficient_index = 0
    logit = model["intercept"]

    for feature, mean, scale in zip(
        model["numeric_features"], model["numeric_mean"], model["numeric_scale"]
    ):
        logit += (float(patient[feature]) - mean) / scale * coefficients[coefficient_index]
        coefficient_index += 1

    for feature, categories in zip(model["categorical_features"], model["categories"]):
        try:
            category_index = categories.index(patient[feature])
        except ValueError:
            pass
        else:
            logit += coefficients[coefficient_index + category_index]
        coefficient_index += len(categories)

    if logit >= 0:
        return 1 / (1 + math.exp(-logit))
    exp_logit = math.exp(logit)
    return exp_logit / (1 + exp_logit)


def _risk_band(pct: float) -> str:
    if pct < 30:
        return "Low"
    if pct < 60:
        return "Medium"
    return "High"


def predict(patient: PatientInput) -> PredictionResponse:
    model = get_model()
    proba = _predict_probability(patient.model_dump(), model)
    pct = round(float(proba) * 100, 1)

    # Optional: if your model/pipeline exposes feature importances,
    # surface the top ones here instead of an empty list.
    top_factors: list[str] = []

    return PredictionResponse(
        readmission_risk_pct=pct,
        risk_band=_risk_band(pct),
        top_factors=top_factors,
        model_version=model["model_version"],
    )
