from code_names_bot_text_graph.semantic_disambiguator.synonym_sense_proposer import SynonymSenseProposer
from code_names_bot_text_graph.semantic_disambiguator.consec_synonym_disambiguator import ConsecSynonymDisambiguator

from config import SYNONYM_SENSE_LABELS, DICTIONARY, SENSE_INVENTORY

import json
from tqdm import tqdm


def main():
    with open(SYNONYM_SENSE_LABELS, "r") as file:
        synonym_sense_labels = json.loads(file.read())
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory = json.loads(file.read())

    sense_proposer = SynonymSenseProposer(sense_inventory)
    disambiguator = ConsecSynonymDisambiguator(dictionary)

    total_correct = 0
    errors = set()

    for sense_id in tqdm(synonym_sense_labels.keys()):
        lemma = dictionary[sense_id]["lemma"]
        pos = dictionary[sense_id]["pos"]
        for synonym in synonym_sense_labels[sense_id]:
            sense_label = synonym_sense_labels[sense_id][synonym]["sense"]
            sense_proposals = sense_proposer.get_senses(lemma, pos)
            predicted_sense = disambiguator.disambiguate(sense_id, sense_proposals)

            if predicted_sense == sense_label:
                total_correct += 1
            else:
                errors.add((lemma, synonym))

    print("Correct: ", total_correct)
    print("Incorrect", len(errors))

    print()
    print(errors)

if __name__ == "__main__":
    main()