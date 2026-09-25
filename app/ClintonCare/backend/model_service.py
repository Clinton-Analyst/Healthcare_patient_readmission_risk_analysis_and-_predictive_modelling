"""
Wraps your trained model. Swap the loading logic and FEATURE_ORDER
to match how your model was actually trained.

Expected model file: backend/model/readmission_model.pkl
Saved with joblib, exposing either:
  - .predict_proba(X) -> returns [:, 1] as the positive-class probability, or
  - .predict(X)        -> returns a probability/score directly

If you trained with a scikit-learn Pipeline that includes your
preprocessing (encoding, scaling), just drop that whole pipeline
in as the pickle -- this file doesn't need to change.
"""

from pathlib import Path
from functools import lru_cache

import joblib
import pandas as pd

from schemas import PatientInput, PredictionResponse

MODEL_PATH = Path(__file__).parent / "model" / "readmission_logistic_model.pkl"
MODEL_VERSION = "1.0.0"

# Column order your model expects. Edit to match your training data.
FEATURE_ORDER = [
    "Age",
    "Length_of_Stay",
    "Previous_Admissions",
    "Previous_ER_Visits",
    "Medication_Count",
    "Lab_Test_Count",
    "Average_Glucose",
    "Systolic_BP",
    "Treatment_Cost",
    "Satsfaction_Score",
    "Gender",
    "Region",
    "Insurance_Type",
    "Hospital_Department",
    "Diabetes",
    "Hypertension",
    "Heart_Disease",
    "Discharge_Type",
    "Followup_Scheduled",
    "Followup_Attended"
]


@lru_cache(maxsize=1)
def get_model():
    """Load once, cache for the life of the process."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No model found at {MODEL_PATH}. "
            "Drop your trained model file there as 'readmission_model.pkl' "
            "(joblib.dump(model, 'readmission_model.pkl'))."
        )
    return joblib.load(MODEL_PATH)


def _to_dataframe(patient: PatientInput) -> pd.DataFrame:
    row = patient.model_dump()
    return pd.DataFrame([row])[FEATURE_ORDER]


def _risk_band(pct: float) -> str:
    if pct < 30:
        return "Low"
    if pct < 60:
        return "Medium"
    return "High"


def predict(patient: PatientInput) -> PredictionResponse:
    model = get_model()
    X = _to_dataframe(patient)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0][1]
    else:
        proba = float(model.predict(X)[0])

    pct = round(float(proba) * 100, 1)

    # Optional: if your model/pipeline exposes feature importances,
    # surface the top ones here instead of an empty list.
    top_factors: list[str] = []

    return PredictionResponse(
        readmission_risk_pct=pct,
        risk_band=_risk_band(pct),
        top_factors=top_factors,
        model_version=MODEL_VERSION,
    )
