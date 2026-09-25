# CareSignal — Patient Prediction

Connects a trained readmission-risk model to the CareSignal "Patient Prediction" screen.

## Structure

```
caresignal/
├── backend/
│   ├── main.py              # FastAPI app, /api/predict endpoint
│   ├── model_service.py     # Loads your model, runs predictions
│   ├── schemas.py           # Request/response validation
│   ├── requirements.txt
│   └── model/
│       └── readmission_model.pkl   # <- put your trained model here
└── frontend/
    ├── index.html           # Matches the Patient Prediction screen
    ├── styles.css
    └── app.js                # Calls the API, renders the result panel
```

## 1. Plug in your model

1. Save your trained model with joblib:
   ```python
   import joblib
   joblib.dump(model, "readmission_model.pkl")
   ```
   If your model needs preprocessing (encoding categorical fields like
   `sex_at_birth` or `admission_type`, scaling numeric fields), save the
   whole `sklearn.Pipeline` (preprocessor + model) as one object — that
   way `model_service.py` doesn't need any changes.

2. Copy the file to `backend/model/readmission_model.pkl`.

3. Open `backend/model_service.py` and check `FEATURE_ORDER` matches the
   column order/names your model was trained on. Rename as needed.

If your model isn't scikit-learn-style (e.g. it's a saved PyTorch/TF
model, or lives behind an existing API you call), only
`model_service.py` needs to change — everything else (schemas, routes,
frontend) stays the same.

## 2. Run the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Check it's alive: `curl http://localhost:8000/api/health`

## 3. Run the frontend

The frontend is plain HTML/CSS/JS — no build step. Just open
`frontend/index.html` in a browser, or serve it:

```bash
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500`.

`app.js` calls `API_BASE_URL` (set to `http://localhost:8000` by
default) — change that constant when you deploy the backend somewhere
real.

## 4. Test end-to-end

Fill in the form (defaults match your screenshot: 67F, Emergency
admission, Heart failure, 6-day stay) and click **Predict readmission
risk**. The result panel updates with the predicted percentage and a
Low/Medium/High risk band, colored to match.

## Deploying

- **Backend**: any host that runs a Python ASGI app (Render, Railway,
  Fly.io, a plain VM behind nginx, AWS/GCP/Azure). Put the model file
  in the same container/image as the code.
- **Frontend**: any static host (Netlify, Vercel, S3+CloudFront, or
  served by the same backend via FastAPI's `StaticFiles`).
- **CORS**: `main.py` currently allows all origins (`allow_origins=["*"]`)
  for easy local development — restrict this to your real frontend
  domain before going to production.
- Since this handles patient health data, make sure hosting, transport
  (HTTPS), and storage meet whatever compliance requirements (e.g.
  HIPAA) apply to your deployment.
