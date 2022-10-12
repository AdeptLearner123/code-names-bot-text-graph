import sys
import random
import time
import json
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from config import SENSE_PROPOSALS, DICTIONARY
from .labeler_window import LabelerWindow

class Labeler:
    def __init__(self, sense_proposals, text_ids, dictionary):
        self._sense_proposals = sense_proposals
        self._text_ids = text_ids
        self._dictionary = dictionary

    def _update(self):
        current_text_id = self._text_ids[self._current]
        tokens, senses, definitions = [], [], []
        
        for sense_proposals in self._sense_proposals[current_text_id]:
            tokens.append(sense_proposals["token"])
            senses.append(sense_proposals["senses"])
            definitions.append([ self._dictionary[sense]["definition"] for sense in sense_proposals["senses"] ])

        self.window.set_text(current_text_id, tokens, senses, definitions)

    @Slot()
    def _next_handler(self):
        self._current = min(self._current + 1, len(self._text_ids) - 1)
        self._update()

    @Slot()
    def _prev_handler(self):
        self._current = max(self._current - 1, 0)
        self._update()

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


def read_sense_proposals():
    with open(SENSE_PROPOSALS, "r") as file:
        sense_proposals = json.loads(file.read())
    return sense_proposals


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())
    return dictionary

def main():
    print("Reading senses")
    start = time.time()
    sense_proposals = read_sense_proposals()
    print("Read time", time.time() - start)
    print("Reading definitions")
    start = time.time()
    dictionary = read_dictionary()
    print("Read time", time.time() - start)

    random.seed(0)
    text_ids = list(sense_proposals.keys())
    random.shuffle(text_ids)

    labeler = Labeler(sense_proposals, text_ids, dictionary)
    labeler.start()

if __name__ == "__main__":
    main()