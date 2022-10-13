from code_names_bot_text_graph.disambiguator.baseline_disambiguator import BaselineDisambiguator

from config import SENSE_LABELS, DICTIONARY, SENSE_PROPOSALS

import json
from enum import Enum
from collections import defaultdict

class ErrorReason(Enum):
    MISSING_SENSE = 0
    INCORRECT_TAG = 1
    MISSING_PROPOSAL = 2
    INCORRECT_DISAMBIGUATION = 3


def process_text(disambiguator, text_id, all_sense_proposals, all_sense_labels, dictionary):
    sense_labels = all_sense_labels[text_id]
    sense_proposals_list = all_sense_proposals[text_id]

    tokens = []
    sense_definitions_list = []

    for sense_proposals in sense_proposals_list:
        sense_definitions = [ (sense, dictionary[sense]["definition"]) for sense in sense_proposals["senses"] ]
        token = sense_proposals["token"]
        tokens.append(token)
        sense_definitions_list.append(sense_definitions)

    predicted_senses = disambiguator.disambiguate(tokens, sense_definitions_list)

    correct = 0
    errors = defaultdict(lambda: [])
    for token, label, predicted_sense in zip(token, sense_labels, predicted_senses):
        if label == None:
            continue

        if label == predicted_sense:
            correct += 1
        elif label not in dictionary:
            errors[ErrorReason.MISSING_SENSE].append((token, text_id))


def main():
    with open(SENSE_LABELS, "r") as file:
        all_sense_labels = json.loads(file.read())
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_PROPOSALS, "r") as file:
        all_sense_proposals = json.loads(file.read())
    
    disambiguator = BaselineDisambiguator()




if __name__ == "__main__":
    main()