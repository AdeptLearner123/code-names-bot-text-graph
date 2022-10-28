from config import DOMAIN_TO_SENSE, CLASS_TO_SENSE, DOMAIN_LABELS, CLASS_LABELS

import json
from tqdm import tqdm


def evaluate(predictions_file, labels_file, title):
    with open(predictions_file, "r") as file:
        predictions = json.loads(file.read())
    
    with open(labels_file, "r") as file:
        labels = json.loads(file.read())

    correct = 0
    total = 0
    failures = []
    for lemma in labels:
        total += 1
        if predictions[lemma] == labels[lemma]:
            correct += 1
        else:
            failures.append((lemma, predictions[lemma], labels[lemma]))

    print(f"=== {title} ===")
    print(f"Score: {correct}/{total} = {correct / total}")
    print()
    print("Failures:")
    for lemma, prediction, label in failures:
        print(f"\t{lemma}  Expected: {label}  Predicted: {prediction}")


def main():
    evaluate(DOMAIN_TO_SENSE, DOMAIN_LABELS, "DOMAINS")
    evaluate(CLASS_TO_SENSE, CLASS_LABELS, "CLASSES")


if __name__ == "__main__":
    main()