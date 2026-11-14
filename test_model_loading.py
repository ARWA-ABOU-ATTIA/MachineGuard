
from pathlib import Path
import joblib

# Locate the saved model
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "artifacts" / "machineguard_model.joblib"

# Load the model artifact
artifact = joblib.load(MODEL_PATH)

# Extract model information
model = artifact["model"]
threshold = artifact["threshold"]
features = artifact["features"]

print("Model loaded successfully!")
print("-" * 40)

print("Model name:", artifact["model_name"])
print("Model version:", artifact["version"])
print("Threshold:", threshold)
print("Features:", features)

print("-" * 40)
print("Model type:", type(model).__name__)
