"""
Request/response models for the Patient Prediction endpoint.

Field names here map 1:1 to the form fields in the CareSignal UI
(Patient details + Utilization & discharge sections).
"""

from typing import Literal
from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    # --- Patient details ---
    Patient_ID: str=Field(..., description="e.g. 'PT001")
    Age: int = Field(..., ge=0, le=120, description="Age in years")
    Gender: Literal["Male", "Female", "Other"]
    Region: Literal["Nairobi", "Eastern", "Rift Valley", "Coast", "Western"]
    Insurance_Type: Literal["Employer", "NHIF", "Cash", "Other"]

    # --- Admission Information ---
    Admission_Type: Literal["Emergency", "Elective","Other"]
    Hospital_Department: Literal["Diabetes Care", "General Medcine", "Cardioloy", "Orthopedics", "Pediatrics"]
    Length_of_Stay: int = Field(..., ge=0, le=30)
    Previous_Amissions: int = Field(..., ge=0, le=30)
    Previous_ER_Visits: int = Field(..., ge=0, le=30)

    # --- Clinical Information ---
    Diabetes: Literal["Yes", "No"]
    Hypertension: Literal["Yes", "No"]
    Heart_Disease: Literal["Yes", "No"]
    Average_Glucose: int = Field(..., ge=0, le=20)
    Systolic_BP: int = Field(..., ge=0, le=200)
    Medication_Count: int = Field(..., ge=0, le=30)
    Lab_Test_Count: int = Field(..., ge=0, le=30)


    # --- Followup Discharge ---
    Followup_Scheduled: Literal["Yes", "No"]
    Followup_Attended: Literal["Yes", "No"]
    Discharge_Type: Literal["Home", "Home with Follow-up", "Other"]
    Treatment_Cost: int = Field(..., ge=0, le=10000000)
    Satisfaction_Score: int = Field(..., ge=0, le=10)

    class Config:
       json_schema_extra = {
            "example": {
                "Age": 67,
                "Gender": "Female",
                "Region": "Eastern",
                "Insurance_Type": "NHIF",
                "Admission_Type": "Emergency",
                "Hospital_Department": "General Medicine",
                "Length_of_Stay": 3,
                "Previous_Admissions": 5,
                "Previous_ER_Visits": 2,
                "Diabetes": "Yes",
                "Hypertension": "Yes",
                "Heart_Disease": "Yes",
                "Average_Glucose": 191.6,
                "Systolic_BP": 130,
                "Medication_Count": 5,
                "Lab_Test_Count": 4,
                "Followup_Scheduled": "Yes",
                "Followup_Attended": "No",
                "Discharge_Type": "Home",
                "Treatment_Cost": 300000,
                "Satisfaction_Score": 4.8
            }
        }


class PredictionResponse(BaseModel):
    readmission_risk_pct: float = Field(..., description="0-100 predicted probability")
    risk_band: Literal["Low", "Medium", "High"]
    top_factors: list[str] = Field(
        default_factory=list,
        description="Optional: human-readable drivers of the score, if the model exposes them",
    )
    model_version: str
