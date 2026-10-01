"""Central configuration for EnergyInvest.

Defines paths, GIPT feature names, label mappings, abstention thresholds,
grouped holdout settings, and reproducibility seed.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "gipt_modeling.csv"
MODEL_PATH = ROOT / "models" / "energyinvest_gipt_model.joblib"
METRICS_PATH = ROOT / "outputs" / "metrics.json"
PREDICTIONS_PATH = ROOT / "outputs" / "holdout_predictions.csv"

TARGET_COL = "target_high_risk"
STATUS_COL = "Status"
GROUP_COL = "GEM location ID"
ID_COL = "GEM unit/phase ID"

NUMERIC_FEATURES = ["Capacity (MW)"]
CATEGORICAL_FEATURES = [
    "Type", "Country/area", "Subregion", "Region", "Technology",
    "Associated storage", "Fuel (combustion only)", "CHP", "CCS",
    "Captive Industry Type", "Location accuracy"
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

HIGH_RISK_STATUSES = {
    "cancelled", "cancelled - inferred 4 y",
    "shelved", "shelved - inferred 2 y"
}
LOW_RISK_STATUSES = {"operating"}
UNRESOLVED_STATUSES = {"announced", "pre-construction", "construction"}

ABSTAIN_LOW = 0.40
ABSTAIN_HIGH = 0.60
HIGH_RISK_THRESHOLD = 0.60
TEST_SIZE = 0.20
RANDOM_STATE = 42
