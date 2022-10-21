import sys
import random
import json

from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.sem_link_disambiguator.mixed_sem_link_disambiguator import MixedSemLinkDisambiguator
from code_names_bot_text_graph.sem_link_disambiguator.sem_link_sense_proposer import SemLinkSenseProposer
from config import DICTIONARY, SEM_LINK_SENSE_LABELS, SENSE_INVENTORY
from .sem_link_labeler_window import SemLinkLabelerWindow
from .labeler import Labeler

class SemLinkLabeler(Labeler):
    def __init__(self, sem_link_sense_proposer, sem_link_disambiguator, window, dictionary, labels, save_labels_handler):
        super().__init__(window, save_labels_handler)
        self._sem_link_sense_proposer = sem_link_sense_proposer
        self._sem_link_disambiguator = sem_link_disambiguator
        self._dictionary = dictionary
        self._labels = labels

    def _update(self, current_key):
        current_lemma = self._dictionary[current_key]["lemma"]
        title = f"{current_lemma} -- {current_key}"
        definition = self._dictionary[current_key]["definition"]

        synonyms = self._dictionary[current_key]["synonyms"]
        domains = self._dictionary[current_key]["domains"]
        classes = self._dictionary[current_key]["classes"]

        linked_lemmas = synonyms + domains + classes
        link_types = ["SYN"] * len(synonyms) + ["DOMAIN"] * len(domains) + ["CLASS"] * len(classes)
        senses_list, predicted_senses, definitions_list, labels = [], [], [], []
        for link_lemma, link_type in zip(linked_lemmas, link_types):
            link_senses = self._sem_link_sense_proposer.propose_senses(current_key, link_lemma, link_type)
            senses_list.append(link_senses)
            predicted_senses.append(self._sem_link_disambiguator.disambiguate(current_key, link_senses, link_type))
            definitions_list.append([ self._dictionary[sense]["definition"] for sense in link_senses ])
            
            if current_key in self._labels and link_lemma in self._labels[current_key]:
                labels.append(self._labels[current_key][link_lemma]["sense"])
            else:
                labels.append(None)

        self._window.set_text(title, definition, linked_lemmas, link_types, senses_list, definitions_list, labels, predicted_senses)

    def _save_labels(self, current_key):
        labels = self._window.get_labels()
        tokens = self._window.get_tokens()
        token_types = self._window.get_token_types()

        labels_dict = { token: { "type": token_type, "sense": sense } for token, token_type, sense in zip(tokens, token_types, labels) }
        self._labels[current_key] = labels_dict
        self._save_labels_handler(self._labels)


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        return json.loads(file.read())


def read_labels():
    with open(SEM_LINK_SENSE_LABELS, "r") as file:
        return json.loads(file.read())


def save_labels(sense_labels):
    with open(SEM_LINK_SENSE_LABELS, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def sense_has_synonyms(sense_id, dictionary):
    entry = dictionary[sense_id]
    return len(entry["synonyms"]) > 0 or len(entry["domains"]) > 0 or len(entry["classes"]) > 0


def main():
    dictionary = read_dictionary()
    sense_labels = read_labels()
    sense_inventory_data = read_sense_inventory()

    sense_inventory = SenseInventory(sense_inventory_data)
    sem_link_sense_proposer = SemLinkSenseProposer(dictionary, sense_inventory)
    sem_link_disambiguator = MixedSemLinkDisambiguator(dictionary)
    labeler = SemLinkLabeler(sem_link_sense_proposer, sem_link_disambiguator, SemLinkLabelerWindow, dictionary, sense_labels, save_labels)

    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        keys = list(sense_labels.keys())
    else:
        keys = list(dictionary.keys())
        keys = [ sense_id for sense_id in keys if sense_has_synonyms(sense_id, dictionary)]
        random.seed(0)
        random.shuffle(keys)
    labeler.start(keys)

if __name__ == "__main__":
    main()