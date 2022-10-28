import sys
import random
import json

from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.synonym_disambiguator.synonym_disambiguator import SynonymDisambiguator
from config import DICTIONARY, DOMAIN_LABELS, CLASS_LABELS, DOMAIN_TO_SENSE, CLASS_TO_SENSE, SENSE_INVENTORY
from .sem_link_labeler_window import SemLinkLabelerWindow
from .labeler import Labeler

class SemLinkLabeler(Labeler):
    def __init__(self, sense_inventory, predictions, labels, window, dictionary, key, save_labels_handler):
        super().__init__(window, save_labels_handler)
        self._sense_inventory = sense_inventory
        self._dictionary = dictionary
        self._predictions = predictions
        self._labels = labels
        self._key = key

    def _update(self, current_lemma):
        title = f"{self._current}: {current_lemma}"

        senses = self._sense_inventory.get_senses_from_lemma_ignore_case(current_lemma)
        definitions = [ self._dictionary[sense]["definition"] for sense in senses ]
        prediction = self._predictions[current_lemma]
        label = self._labels[current_lemma] if current_lemma in self._labels else None

        examples = []
        for entry in self._dictionary.values():
            if current_lemma in entry[self._key]:
                examples.append(entry["lemma"])
                if len(examples) > 3:
                    break

        self._window.set_text(title, current_lemma, senses, definitions, label, prediction, examples)

    def _save_labels(self, current_lemma):
        label = self._window.get_label()
        self._labels[current_lemma] = label
        self._save_labels_handler(self._labels)


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        return json.loads(file.read())


def read_json(file):
    with open(file, "r") as file:
        return json.loads(file.read())


def save_labels(labels_file, sense_labels):
    with open(labels_file, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def label(labels_file, predictions_file, key):
    dictionary = read_dictionary()
    sense_labels = read_json(labels_file)
    predictions = read_json(predictions_file)
    sense_inventory_data = read_sense_inventory()

    sense_inventory = SenseInventory(sense_inventory_data)
    save_labels_handler = lambda labels: save_labels(labels_file, labels)
    labeler = SemLinkLabeler(sense_inventory, predictions, sense_labels, SemLinkLabelerWindow, dictionary, key, save_labels_handler)

    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        keys = list(sense_labels.keys())
    else:
        keys = list(predictions.keys())
        random.seed(0)
        random.shuffle(keys)
    labeler.start(keys)


def label_domains():
    label(DOMAIN_LABELS, DOMAIN_TO_SENSE, "domains")


def label_classes():
    label(CLASS_LABELS, CLASS_TO_SENSE, "classes")