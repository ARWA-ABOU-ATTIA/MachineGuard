
from pathlib import Path
import math

import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


# --------------------------------------------------
# 1. Load trained model
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "machineguard_model.joblib"

artifact = joblib.load(MODEL_PATH)

model = artifact["model"]
THRESHOLD = artifact["threshold"]
FEATURES = artifact["features"]


# --------------------------------------------------
# 2. Initialize FastAPI
# --------------------------------------------------

app = FastAPI(
    title="MachineGuard API",
    description="Machine Failure Risk Assessment System",
    version="1.0.0"
)


# --------------------------------------------------
# 3. Define input schema
# --------------------------------------------------

class MachineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    air_temperature: float = Field(gt=0)
    process_temperature: float = Field(gt=0)
    rotational_speed: float = Field(gt=0)
    torque: float = Field(gt=0)
    tool_wear: float = Field(ge=0)
    machine_type: Literal["L", "M", "H"]


# --------------------------------------------------
# 4. Define prediction response
# --------------------------------------------------

class PredictionResponse(BaseModel):
    failure_score: float
    threshold: float
    prediction: int
    status: str


# --------------------------------------------------
# 5. Health check endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": artifact["model_name"],
        "version": artifact["version"]
    }


# --------------------------------------------------
# 6. Prediction endpoint
# --------------------------------------------------

@app.post("/predict", response_model=PredictionResponse)
def predict_failure(data: MachineInput):

    # Calculate engineered feature
    power = (
        data.torque *
        data.rotational_speed *
        (2 * math.pi / 60)
    )

    # Prepare input data
    input_data = pd.DataFrame([{
        "Air temperature": data.air_temperature,
        "Process temperature": data.process_temperature,
        "Rotational speed": data.rotational_speed,
        "Torque": data.torque,
        "Tool wear": data.tool_wear,
        "Power": power,
        "Type": data.machine_type
    }])

    # Ensure the same feature order used during training
    input_data = input_data[FEATURES]

    # Predict failure probability
    failure_score = float(
        model.predict_proba(input_data)[0, 1]
    )

    # Apply the selected decision threshold
    prediction = int(failure_score >= THRESHOLD)

    status = (
        "Failure Risk Detected"
        if prediction == 1
        else "No Failure Risk Detected"
    )

    return {
        "failure_score": round(failure_score, 6),
        "threshold": THRESHOLD,
        "prediction": prediction,
        "status": status
    }
