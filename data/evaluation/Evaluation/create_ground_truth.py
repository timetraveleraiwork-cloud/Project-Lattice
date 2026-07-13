import json
from pathlib import Path

PREDICTIONS = Path("Week3/Staging/raw_extractions.json")
GROUND_TRUTH_DIR = Path("Week3/Evaluation/ground_truth")

GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

with open(PREDICTIONS, "r", encoding="utf-8") as f:
    predictions = json.load(f)

for prediction in predictions:
    filename = prediction["document"].replace(".txt", ".json")

    with open(GROUND_TRUTH_DIR / filename, "w", encoding="utf-8") as out:
        json.dump(prediction, out, indent=4)

print(f"Created {len(predictions)} ground truth files.")
