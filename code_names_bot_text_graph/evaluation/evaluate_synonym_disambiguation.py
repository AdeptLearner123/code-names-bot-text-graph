from config import SYNONYM_LABELS, SENSE_INVENTORY, DICTIONARY

import json
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.synonym_disambiguator.synonym_disambiguator import SynonymDisambiguator


def main():
    with open(SYNONYM_LABELS, "r") as file:
        synonym_labels = json.loads(file.read())
    
    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())

    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    sense_inventory = SenseInventory(sense_inventory_data)
    synonym_disambiguator = SynonymDisambiguator(dictionary)

    correct = 0
    total = 0
    failures = []
    for sense in synonym_labels:
        pos = dictionary[sense]["pos"]
        for synonym in synonym_labels[sense]:
            label = synonym_labels[sense][synonym]
            if label is None:
                continue

            possible_senses = sense_inventory.get_senses_from_lemma(synonym, pos)
            prediction = synonym_disambiguator.disambiguate(sense, possible_senses)

            total += 1
            if prediction == label:
                correct += 1
            else:
                failures.append((sense, synonym, prediction, label))

    print(f"Score: {correct}/{total} = {correct / total}")
    print()
    print("Failures:")
    for sense, synonym, prediction, label in failures:
        print(f"\t{sense} - {synonym}  Expected: {label}  Predicted: {prediction}")


if __name__ == "__main__":
    main()