import json
from pathlib import Path


GROUND_TRUTH_DIR = Path("Week3/Evaluation/ground_truth")
PREDICTION_DIR = Path("Week3/Staging")
RESULTS_DIR = Path("Week3/Evaluation/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_predictions():
    predictions = load_json(PREDICTION_DIR / "raw_extractions.json")

    prediction_map = {}

    for prediction in predictions:
        json_name = prediction["document"].replace(".txt", ".json")
        prediction_map[json_name] = prediction

    return prediction_map


def normalize_entity(entity):
    return (
        entity["type"].strip().lower(),
        entity["name"].strip().lower(),
    )


def normalize_relationship(rel):
    return (
        rel["source"].strip().lower(),
        rel["relation"].strip().lower(),
        rel["target"].strip().lower(),
    )


def compare_entities(gt_entities, pred_entities):
    gt = {normalize_entity(entity) for entity in gt_entities}
    pred = {normalize_entity(entity) for entity in pred_entities}

    tp = gt & pred
    fp = pred - gt
    fn = gt - pred

    return {
        "tp": len(tp),
        "fp": len(fp),
        "fn": len(fn),
        "true_positives": sorted(tp),
        "false_positives": sorted(fp),
        "false_negatives": sorted(fn),
    }


def compare_relationships(gt_relationships, pred_relationships):
    gt = {normalize_relationship(rel) for rel in gt_relationships}
    pred = {normalize_relationship(rel) for rel in pred_relationships}

    tp = gt & pred
    fp = pred - gt
    fn = gt - pred

    return {
        "tp": len(tp),
        "fp": len(fp),
        "fn": len(fn),
        "true_positives": sorted(tp),
        "false_positives": sorted(fp),
        "false_negatives": sorted(fn),
    }


def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return precision, recall, f1


def main():
    total_entity_tp = total_entity_fp = total_entity_fn = 0
    total_rel_tp = total_rel_fp = total_rel_fn = 0

    prediction_map = load_predictions()

    EVALUATION_SET = [
        "001_employee_bio.json",
        "010_vendor_agreement.json",
        "015_email_thread.json",
        "023_project_memo.json",
        "030_incident_report.json",
    ]

    for filename in EVALUATION_SET:
        gt_file = GROUND_TRUTH_DIR / filename
        gt = load_json(gt_file)

        pred = prediction_map.get(gt_file.name)

        if pred is None:
            print(f"Prediction missing: {gt_file.name}")
            continue

        entity_results = compare_entities(
            gt["entities"],
            pred["entities"],
        )

        relationship_results = compare_relationships(
            gt["relationships"],
            pred["relationships"],
        )

        total_entity_tp += entity_results["tp"]
        total_entity_fp += entity_results["fp"]
        total_entity_fn += entity_results["fn"]

        total_rel_tp += relationship_results["tp"]
        total_rel_fp += relationship_results["fp"]
        total_rel_fn += relationship_results["fn"]

        print("=" * 60)
        print(gt_file.name)

        print("\nEntities")
        print(f"TP : {entity_results['tp']}")
        print(f"FP : {entity_results['fp']}")
        print(f"FN : {entity_results['fn']}")

        print("\nRelationships")
        print(f"TP : {relationship_results['tp']}")
        print(f"FP : {relationship_results['fp']}")
        print(f"FN : {relationship_results['fn']}")

    entity_precision, entity_recall, entity_f1 = calculate_metrics(
        total_entity_tp,
        total_entity_fp,
        total_entity_fn,
    )

    rel_precision, rel_recall, rel_f1 = calculate_metrics(
        total_rel_tp,
        total_rel_fp,
        total_rel_fn,
    )

    print("\n" + "=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)

    print("\nEntities")
    print(f"Precision : {entity_precision:.2%}")
    print(f"Recall    : {entity_recall:.2%}")
    print(f"F1 Score  : {entity_f1:.2%}")

    print("\nRelationships")
    print(f"Precision : {rel_precision:.2%}")
    print(f"Recall    : {rel_recall:.2%}")
    print(f"F1 Score  : {rel_f1:.2%}")

    results = {
        "entities": {
            "precision": entity_precision,
            "recall": entity_recall,
            "f1": entity_f1,
            "tp": total_entity_tp,
            "fp": total_entity_fp,
            "fn": total_entity_fn,
        },
        "relationships": {
            "precision": rel_precision,
            "recall": rel_recall,
            "f1": rel_f1,
            "tp": total_rel_tp,
            "fp": total_rel_fp,
            "fn": total_rel_fn,
        },
    }

    with open(
        RESULTS_DIR / "results.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(results, f, indent=4)

    print("\nSaved evaluation to Evaluation/results/results.json")


if __name__ == "__main__":
    main()
