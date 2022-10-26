from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.sem_link_disambiguator.mixed_sem_link_disambiguator import ConsecSemLinkDisambiguator
from code_names_bot_text_graph.sem_link_disambiguator.sem_link_sense_proposer import SemLinkSenseProposer

from config import SEM_LINK_SENSE_LABELS, DICTIONARY, SENSE_INVENTORY

import json
from tqdm import tqdm


def main():
    with open(SEM_LINK_SENSE_LABELS, "r") as file:
        sem_link_sense_labels = json.loads(file.read())
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())

    sense_inventory = SenseInventory(sense_inventory_data)
    sem_link_sense_proposer = SemLinkSenseProposer(dictionary, sense_inventory)
    disambiguator = ConsecSemLinkDisambiguator(dictionary)

    total_correct = 0
    errors = set()

    for sense_id in tqdm(sem_link_sense_labels.keys()):
        for sem_link_lemma in sem_link_sense_labels[sense_id]:
            sem_link_label = sem_link_sense_labels[sense_id][sem_link_lemma]["sense"]
            sem_link_type = sem_link_sense_labels[sense_id][sem_link_lemma]["type"]

            sem_link_senses = sem_link_sense_proposer.propose_senses(sense_id, sem_link_lemma, sem_link_type)
            predicted_sense = disambiguator.disambiguate(sense_id, sem_link_senses, sem_link_type)

            if predicted_sense == sem_link_label:
                total_correct += 1
            else:
                lemma = dictionary[sense_id]["lemma"]
                errors.add((lemma, sem_link_lemma))

    print("Correct: ", total_correct)
    print("Incorrect", len(errors))

    print()
    print(errors)

if __name__ == "__main__":
    main()