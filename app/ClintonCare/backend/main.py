from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PatientInput, PredictionResponse
import model_service

app = FastAPI(title="CareSignal Readmission API", version="1.0.0")

# Allow the frontend (served from a different origin/port while developing)
# to call this API. Tighten this to your real domain before going to prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/predict", response_model=PredictionResponse)
def predict(patient: PatientInput):
    try:
        return model_service.predict(patient)
    except FileNotFoundError as e:
        # Model file hasn't been placed in backend/model/ yet
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# Run with: uvicorn main:app --reload --port 8000
