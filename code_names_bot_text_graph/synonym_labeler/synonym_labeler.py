import sys
import random
import json
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from code_names_bot_text_graph.semantic_disambiguator.synonym_sense_proposer import SynonymSenseProposer
from code_names_bot_text_graph.semantic_disambiguator.baseline_synonym_disambiguator import BaselineSynonymDisambiguator
from code_names_bot_text_graph.semantic_disambiguator.synonym_disambiguator import SynonymDisambiguator
from config import DICTIONARY, SYNONYM_SENSE_LABELS, SENSE_INVENTORY
from .synonym_labeler_window import SynonymLabelerWindow

class SynonymLabeler:
    def __init__(self, sense_proposer, disambiguator, synonym_disambiguator, sense_ids, dictionary, labels, save_labels_handler):
        self._sense_proposer = sense_proposer
        self._disambiguator = disambiguator
        self._synonym_disambiguator = synonym_disambiguator
        self._sense_ids = sense_ids
        self._dictionary = dictionary
        self._labels = labels
        self._save_labels_handler = save_labels_handler

    def _update(self):
        current_sense_id = self._sense_ids[self._current]
        current_lemma = self._dictionary[current_sense_id]["lemma"]
        title = f"{current_lemma} -- {current_sense_id}"
        pos = self._dictionary[current_sense_id]["pos"]
        definition = self._dictionary[current_sense_id]["definition"]

        synonyms = self._dictionary[current_sense_id]["synonyms"]
        domains = self._dictionary[current_sense_id]["domains"]
        classes = self._dictionary[current_sense_id]["classes"]

        tokens = synonyms + domains + classes
        token_types = ["SYN"] * len(synonyms) + ["DOMAIN"] * len(domains) + ["CLASS"] * len(classes)
        token_senses, predicted_senses, definitions_list, labels = [], [], [], []
        for token, token_type in zip(tokens, token_types):
            if token_type == "SYN":
                senses = self._sense_proposer.get_senses(token, pos)
                token_senses.append(senses)
                predicted_senses.append(self._synonym_disambiguator.disambiguate(current_sense_id, senses))
            else:
                senses = self._sense_proposer.get_senses(token, "noun")
                token_senses.append(senses)
                predicted_senses.append(self._disambiguator.disambiguate(current_sense_id, senses))
            definitions_list.append([ self._dictionary[sense]["definition"] for sense in senses ])
            
            if current_sense_id in self._labels and token in self._labels[current_sense_id]:
                labels.append(self._labels[current_sense_id][token]["sense"])
            else:
                labels.append(None)

        self.window.set_text(title, definition, tokens, token_types, token_senses, definitions_list, labels, predicted_senses)

    @Slot()
    def _next_handler(self):
        self._save_labels()
        self._current = min(self._current + 1, len(self._sense_ids) - 1)
        self._update()

    @Slot()
    def _prev_handler(self):
        self._save_labels()
        self._current = max(self._current - 1, 0)
        self._update()
    
    def _save_labels(self):
        current_sense_id = self._sense_ids[self._current]
        labels = self.window.get_labels()
        tokens = self.window.get_tokens()
        token_types = self.window.get_token_types()

        labels_dict = { token: { "type": token_type, "sense": sense } for token, token_type, sense in zip(tokens, token_types, labels) }
        self._labels[current_sense_id] = labels_dict
        self._save_labels_handler(self._labels)

    def start(self, current = 0):
        self._current = current

        app = QtWidgets.QApplication([])

        self.window = SynonymLabelerWindow()
        self.window.resize(800, 600)
        self.window.show()

        self._update()
        self.window.next_signal.connect(self._next_handler)
        self.window.prev_signal.connect(self._prev_handler)
        sys.exit(app.exec())


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        return json.loads(file.read())


def read_labels():
    with open(SYNONYM_SENSE_LABELS, "r") as file:
        return json.loads(file.read())


def save_labels(sense_labels):
    with open(SYNONYM_SENSE_LABELS, "w+") as file:
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
    sense_inventory = read_sense_inventory()

    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        sense_ids = list(sense_labels.keys())
    else:
        sense_ids = list(dictionary.keys())
        sense_ids = [ sense_id for sense_id in sense_ids if sense_has_synonyms(sense_id, dictionary)]
        random.seed(0)
        random.shuffle(sense_ids)

    sense_proposer = SynonymSenseProposer(sense_inventory)
    disambiguator = BaselineSynonymDisambiguator(dictionary)
    synonym_disambiguator = SynonymDisambiguator(dictionary)
    labeler = SynonymLabeler(sense_proposer, disambiguator, synonym_disambiguator, sense_ids, dictionary, sense_labels, save_labels)
    labeler.start()

if __name__ == "__main__":
    main()