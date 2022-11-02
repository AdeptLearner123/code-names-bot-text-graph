import sys
import random
import json

from code_names_bot_text_graph.text_disambiguator.text_sense_proposer import TextSenseProposer
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.text_disambiguator.consec_text_disambiguator import ConsecTextDisambiguator
from code_names_bot_text_graph.text_disambiguator.consec_compound_text_disambiguator import ConsecCompoundTextDisambiguator
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from config import DICTIONARY, TEXT_SENSE_LABELS, TEXT_LIST, SENSE_INVENTORY
from .text_labeler_window import TextLabelerWindow
from .labeler import Labeler

class TextLabeler(Labeler):
    def __init__(self, token_tagger, sense_proposer, disambiguator, window, text_dict, dictionary, labels, save_labels_handler):
        super().__init__(window, save_labels_handler)
        self._token_tagger = token_tagger
        self._sense_proposer = sense_proposer
        self._disambiguator = disambiguator
        self._text_dict = text_dict
        self._dictionary = dictionary
        self._labels = labels

    def _update(self, current_key):
        # Extract sense id from text id so that we can display the lemma in the title
        current_sense_id = current_key.replace("_def", "|").replace("_text", "|").split("|")[0]
        current_lemma = self._dictionary[current_sense_id]["lemma"]
        title = f"{self._current}: {current_lemma} -- {current_key}"

        text = self._text_dict[current_key]
        token_tags = self._token_tagger.tokenize_tag(text)
        token_senses, compound_indices = self._sense_proposer.propose_senses(token_tags)
        predicted_senses = self._disambiguator.disambiguate(token_senses, compound_indices)

        tokens, senses_list, definitions_list = [], [], []
        
        for token, senses in token_senses:
            tokens.append(token)
            senses_list.append(senses)
            definitions_list.append([ self._dictionary[sense]["definition"] for sense in senses ])

        labels = self._labels[current_key] if current_key in self._labels else [None] * len(tokens)
        self._window.set_text(title, tokens, senses_list, definitions_list, labels, predicted_senses)

    def _save_labels(self, current_key):
        self._labels[current_key] = self._window.get_labels()
        self._save_labels_handler(self._labels)


def read_dictionary():
    with open(DICTIONARY, "r") as file:
        return json.loads(file.read())


def read_labels():
    with open(TEXT_SENSE_LABELS, "r") as file:
        return json.loads(file.read())


def read_text_dict():
    with open(TEXT_LIST) as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        return { line[0]: line[1] for line in lines }


def save_labels(sense_labels):
    print("Total sense labels", len(sense_labels))
    with open(TEXT_SENSE_LABELS, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def main():
    dictionary = read_dictionary()
    sense_labels = read_labels()
    text_dict = read_text_dict()
    sense_inventory_data = read_sense_inventory()

    token_tagger = TokenTagger()
    sense_inventory = SenseInventory(sense_inventory_data)
    sense_proposer = TextSenseProposer(sense_inventory)
    disambiguator = ConsecCompoundTextDisambiguator(dictionary)
    labeler = TextLabeler(token_tagger, sense_proposer, disambiguator, TextLabelerWindow, text_dict, dictionary, sense_labels, save_labels)


    if len(sys.argv) > 1 and sys.argv[1] == "-l":
        keys = list(sense_labels.keys())
        start = 6
    else:
        keys = list(text_dict.keys())
        random.seed(0)
        random.shuffle(keys)

        start = 0
        while keys[start] in sense_labels:
            start += 1

    labeler.start(keys, start=start)

if __name__ == "__main__":
    main()