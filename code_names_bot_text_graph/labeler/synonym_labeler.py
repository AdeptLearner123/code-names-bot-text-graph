import sys
import random
import json

from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.synonym_disambiguator.synonym_disambiguator import SynonymDisambiguator
from config import DICTIONARY, SYNONYM_LABELS, SENSE_INVENTORY
from .synonym_labeler_window import SynonymLabelerWindow
from .labeler import Labeler

class SemLinkLabeler(Labeler):
    def __init__(self, sense_inventory, synonym_disambiguator, window, dictionary, labels, save_labels_handler):
        super().__init__(window, save_labels_handler)
        self._sense_inventory = sense_inventory
        self._synonym_disambiguator = synonym_disambiguator
        self._dictionary = dictionary
        self._labels = labels

    def _update(self, current_sense):
        current_lemma = self._dictionary[current_sense]["lemma"]
        title = f"{current_lemma} -- {current_sense}"
        definition = self._dictionary[current_sense]["definition"]
        pos = self._dictionary[current_sense]["pos"]

        synonyms = self._dictionary[current_sense]["synonyms"]

        senses_list, predicted_senses, definitions_list, labels = [], [], [], []
        for synonym in synonyms:
            synonym_senses = self._sense_inventory.get_senses_from_lemma(synonym, pos)
            senses_list.append(synonym_senses)
            predicted_senses.append(self._synonym_disambiguator.disambiguate(current_sense, synonym_senses))
            definitions_list.append([ self._dictionary[sense]["definition"] for sense in synonym_senses ])
            
            if current_sense in self._labels and synonym in self._labels[current_sense]:
                labels.append(self._labels[current_sense][synonym])
            else:
                labels.append(None)

        self._window.set_text(title, definition, synonyms, senses_list, definitions_list, labels, predicted_senses)

    def _save_labels(self, current_key):
        labels = self._window.get_labels()
        tokens = self._window.get_tokens()

        labels_dict = { token: label for token, label in zip(tokens, labels) }
        self._labels[current_key] = labels_dict
        self._save_labels_handler(self._labels)


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        return json.loads(file.read())


def read_labels():
    with open(SYNONYM_LABELS, "r") as file:
        return json.loads(file.read())


def save_labels(sense_labels):
    with open(SYNONYM_LABELS, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def sense_has_synonyms(sense_id, dictionary):
    entry = dictionary[sense_id]
    return len(entry["synonyms"]) > 0


def main():
    dictionary = read_dictionary()
    sense_labels = read_labels()
    sense_inventory_data = read_sense_inventory()

    sense_inventory = SenseInventory(sense_inventory_data)
    synonym_disambiguator = SynonymDisambiguator(dictionary)
    labeler = SemLinkLabeler(sense_inventory, synonym_disambiguator, SynonymLabelerWindow, dictionary, sense_labels, save_labels)

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