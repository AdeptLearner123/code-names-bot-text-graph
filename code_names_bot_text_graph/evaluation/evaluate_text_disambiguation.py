from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.text_disambiguator.text_sense_proposer import TextSenseProposer
from code_names_bot_text_graph.text_disambiguator.consec_text_disambiguator import ConsecTextDisambiguator
from code_names_bot_text_graph.text_disambiguator.consec_compound_text_disambiguator import ConsecCompoundTextDisambiguator
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
#from code_names_bot_text_graph.disambiguator.baseline_disambiguator import BaselineDisambiguator

from config import TEXT_LIST, TEXT_SENSE_LABELS, DICTIONARY, SENSE_INVENTORY

import json
from enum import Enum
from collections import defaultdict
from tqdm import tqdm

class ErrorReason(Enum):
    MISSING_SENSE = 0
    INCORRECT_TAG = 1
    MISSING_PROPOSAL = 2
    INCORRECT_DISAMBIGUATION = 3

BATCH_SIZE = 1

def evaluate_text(text_id, text, token_tagger, sense_proposer, disambiguator, sense_labels, dictionary):
    token_tags = token_tagger.tokenize_tag(text)
    token_senses, compound_indices = sense_proposer.propose_senses(token_tags)
    predicted_senses = disambiguator.disambiguate(token_senses, compound_indices)

    correct = 0
    errors = defaultdict(lambda: [])

    for i, (predicted_sense, label) in enumerate(zip(predicted_senses, sense_labels)):
        if label == None:
            continue

        token, tag = token_tags[i]
        _, proposed_senses = token_senses[i]

        if label == predicted_sense:
            correct += 1
        elif label in proposed_senses:
            errors[ErrorReason.INCORRECT_DISAMBIGUATION].append((text_id, token))
        elif label in dictionary and dictionary[label]["pos"] == tag:
            errors[ErrorReason.MISSING_PROPOSAL].append((text_id, token))
        elif label in dictionary:
            errors[ErrorReason.INCORRECT_TAG].append((text_id, token))
        else:
            errors[ErrorReason.MISSING_SENSE].append((text_id, token))
    
    return correct, errors


def evaluate(text_dict, token_tagger, sense_proposer, disambiguator, all_sense_labels, dictionary):
    total_correct = 0
    total_incorrect = 0
    all_errors = defaultdict(lambda: [])

    text_ids = list(all_sense_labels.keys())
    for text_id in tqdm(text_ids):
        correct, errors = evaluate_text(text_id, text_dict[text_id], token_tagger, sense_proposer, disambiguator, all_sense_labels[text_id], dictionary)
            
        total_correct += correct
        for error_type in errors:
            all_errors[error_type] += errors[error_type]
            total_incorrect += len(errors[error_type])
            
    return total_correct, total_incorrect, all_errors


def batch_evaluate_text(text_ids, text_dict, token_tagger, sense_proposer, disambiguator, all_labels, dictionary):
    text_list = [ text_dict[text_id] for text_id in text_ids ]
    labels_list = [ all_labels[text_id] for text_id in text_ids ]

    token_senses_list = []
    compound_indices_list = []
    token_tags_list = []
    for text in text_list:
        token_tags = token_tagger.tokenize_tag(text)
        token_tags_list.append(token_tags)
        token_senses, compound_indices = sense_proposer.propose_senses(token_tags)
        token_senses_list.append(token_senses)
        compound_indices_list.append(compound_indices)
    
    correct = 0
    errors = defaultdict(lambda: [])

    senses_list = disambiguator.batch_disambiguate(list(zip(token_senses_list, compound_indices_list)))
    for text_id, predicted_senses, labels_list, token_tags, token_senses in zip(text_ids, senses_list, labels_list, token_tags_list, token_senses_list):
        for predicted_sense, label, (token, tag), (_, proposed_senses) in zip(predicted_senses, labels_list, token_tags, token_senses):
            if label == None:
                continue

            if label == predicted_sense:
                correct += 1
            elif label in proposed_senses:
                errors[ErrorReason.INCORRECT_DISAMBIGUATION].append((text_id, token))
            elif label in dictionary and dictionary[label]["pos"] == tag:
                errors[ErrorReason.MISSING_PROPOSAL].append((text_id, token))
            elif label in dictionary:
                errors[ErrorReason.INCORRECT_TAG].append((text_id, token))
            else:
                errors[ErrorReason.MISSING_SENSE].append((text_id, token))
    
    return correct, errors


def batch_evaluate(text_dict, token_tagger, sense_proposer, disambiguator, all_sense_labels, dictionary):
    total_correct = 0
    total_incorrect = 0
    all_errors = defaultdict(lambda: [])

    text_ids = list(all_sense_labels.keys())
    with tqdm(total = len(text_ids)) as pbar:
        for i in range(0, len(text_ids), BATCH_SIZE):
            batch_text_ids = text_ids[i : i + BATCH_SIZE]
            correct, errors = batch_evaluate_text(batch_text_ids, text_dict, token_tagger, sense_proposer, disambiguator, all_sense_labels, dictionary)
                
            total_correct += correct
            for error_type in errors:
                all_errors[error_type] += errors[error_type]
                total_incorrect += len(errors[error_type])
            
            pbar.update(BATCH_SIZE)
    
    return total_correct, total_incorrect, all_errors


def main():
    with open(TEXT_SENSE_LABELS, "r") as file:
        all_sense_labels = json.loads(file.read())
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())

    with open(TEXT_LIST, "r") as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        text_dict = { line[0]: line[1] for line in lines }

    token_tagger = TokenTagger()
    sense_inventory = SenseInventory(sense_inventory_data)
    sense_proposer = TextSenseProposer(sense_inventory)
    disambiguator = ConsecCompoundTextDisambiguator(dictionary)

    total_correct, total_incorrect, all_errors = evaluate(text_dict, token_tagger, sense_proposer, disambiguator, all_sense_labels, dictionary)

    print("Correct: ", total_correct)
    print("Incorrect", total_incorrect)

    print()
    print("Errors by type:")
    for error_type in all_errors:
        print(f"{error_type}:  {len(all_errors[error_type])}")
    
    print()
    print("List of errors")
    for error_type in all_errors:
        print(error_type)
        for text_id, token in all_errors[error_type]:
            print(f"\t{text_id}:  {token}")


if __name__ == "__main__":
    main()