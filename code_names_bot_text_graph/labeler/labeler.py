import sys
import random
import json
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from code_names_bot_text_graph.sense_proposal.sense_proposer import SenseProposer
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from config import DICTIONARY, SENSE_LABELS, TEXT_LIST, SENSE_INVENTORY
from .labeler_window import LabelerWindow

class Labeler:
    def __init__(self, token_tagger, sense_proposer, text_ids, text_dict, dictionary, labels, save_labels_handler):
        self._token_tagger = token_tagger
        self._sense_proposer = sense_proposer
        self._text_ids = text_ids
        self._text_dict = text_dict
        self._dictionary = dictionary
        self._labels = labels
        self._save_labels_handler = save_labels_handler

    def _update(self):
        current_text_id = self._text_ids[self._current]
        current_sense_id = current_text_id.replace("_def", "|").replace("_text", "|").split("|")[0]
        current_lemma = self._dictionary[current_sense_id]["lemma"]
        title = f"{current_lemma} -- {current_text_id}"

        text = self._text_dict[current_text_id]
        token_tags = self._token_tagger.tokenize_tag(text)
        token_senses = self._sense_proposer.propose_senses(token_tags)

        tokens, senses_list, definitions_list = [], [], []
        
        for token, senses in token_senses:
            tokens.append(token)
            senses_list.append(senses)
            definitions_list.append([ self._dictionary[sense]["definition"] for sense in senses ])

        labels = self._labels[current_text_id] if current_text_id in self._labels else [None] * len(tokens)

        self.window.set_text(title, tokens, senses_list, definitions_list, labels)

    @Slot()
    def _next_handler(self):
        self._save_labels()
        self._current = min(self._current + 1, len(self._text_ids) - 1)
        self._update()

    @Slot()
    def _prev_handler(self):
        self._save_labels()
        self._current = max(self._current - 1, 0)
        self._update()
    
    def _save_labels(self):
        current_text_id = self._text_ids[self._current]
        self._labels[current_text_id] = self.window.get_labels()
        self._save_labels_handler(self._labels)

    def start(self, current = 0):
        self._current = current

        app = QtWidgets.QApplication([])

        self.window = LabelerWindow()
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
    with open(SENSE_LABELS, "r") as file:
        return json.loads(file.read())


def read_text_dict():
    with open(TEXT_LIST) as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        return { line[0]: line[1] for line in lines }


def save_labels(sense_labels):
    with open(SENSE_LABELS, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def main():
    dictionary = read_dictionary()
    sense_labels = read_labels()
    text_dict = read_text_dict()
    sense_inventory = read_sense_inventory()

    random.seed(0)
    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        text_ids = list(sense_labels.keys())
    else:
        text_ids = list(text_dict.keys())
    random.shuffle(text_ids)

    token_tagger = TokenTagger()
    sense_proposer = SenseProposer(sense_inventory)
    labeler = Labeler(token_tagger, sense_proposer, text_ids, text_dict, dictionary, sense_labels, save_labels)
    labeler.start()

if __name__ == "__main__":
    main()