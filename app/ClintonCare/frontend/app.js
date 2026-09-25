// Point this at your deployed backend when you go live
// (e.g. "https://api.caresignal.yourdomain.com")
const API_BASE_URL = "http://localhost:8000";

const form = document.getElementById("prediction-form");
const submitBtn = document.getElementById("submit-btn");
const resultEmpty = document.getElementById("result-empty");
const resultBody = document.getElementById("result-body");
const resultError = document.getElementById("result-error");
const riskPct = document.getElementById("risk-pct");
const riskBand = document.getElementById("risk-band");
const resultEyebrow = document.getElementById("result-eyebrow");
const topFactorsEl = document.getElementById("top-factors");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  const payload = {
    Age: Number(formData.get("Age")),
    Length_of_Stay: Number(formData.get("Length_of_Stay") || 0),
    Previous_Admissions: Number(formData.get("Previous_Admissions") || 0),
    Previous_ER_Visits: Number(formData.get("Previous_ER_Visits") || 0),
    Medication_Count: Number(formData.get("Medication_Count")),
    Lab_Test_Count: Number(formData.get("Lab_Test_Count") || 0),
    Average_Glucose: Number(formData.get("Average_Glucose") || 0),
    Systolic_BP: Number(formData.get("Systolic_BP") || 0),
    Treatment_Cost: Number(formData.get("Treatment_Cost") || 0),
    Satisfaction_Score: Number(formData.get("Satisfaction_Score") || 0),
    Gender: formData.get("Gender"),
    Region: formData.get("Region"),
    Insurance_Type: formData.get("Insurance_Type"),
    Hospital_Department: formData.get("Hospital_Department"),
    Diabetes: formData.get("Diabetes"),
    Hypertension: formData.get("Hypertension"),
    Heart_Disease: formData.get("Heart_Disease"),
    Discharge_Type: formData.get("Discharge_Type"),
    Followup_Scheduled: formData.get("Followup_Scheduled"),
    Followup_Attended: formData.get("Followup_Attended")
  };

  setLoading(true);
  hide(resultError);

  try {
    const res = await fetch(`${API_BASE_URL}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }

    const data = await res.json();
    renderResult(data);
  } catch (err) {
    hide(resultBody);
    hide(resultEmpty);
    resultError.textContent = err.message || "Something went wrong. Please try again.";
    show(resultError);
  } finally {
    setLoading(false);
  }
});

function renderResult(data) {
  hide(resultEmpty);
  hide(resultError);
  show(resultBody);

  resultEyebrow.textContent = "Predicted result";
  riskPct.textContent = `${data.readmission_risk_pct}%`;
  riskBand.textContent = `${data.risk_band} risk`;

  resultBody.classList.remove("band-low", "band-medium", "band-high");
  resultBody.classList.add(`band-${data.risk_band.toLowerCase()}`);

  topFactorsEl.innerHTML = "";
  if (data.top_factors && data.top_factors.length) {
    const title = document.createElement("p");
    title.style.cssText = "font-size:13px;font-weight:700;margin:14px 0 6px;";
    title.textContent = "Top contributing factors";
    topFactorsEl.appendChild(title);

    const list = document.createElement("ul");
    list.style.cssText = "margin:0;padding-left:18px;font-size:13px;color:#384845;";
    data.top_factors.forEach((f) => {
      const li = document.createElement("li");
      li.textContent = f;
      list.appendChild(li);
    });
    topFactorsEl.appendChild(list);
  }
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading ? "Predicting…" : "Predict readmission risk";
}

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }
