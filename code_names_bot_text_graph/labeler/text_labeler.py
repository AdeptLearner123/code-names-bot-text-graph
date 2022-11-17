import random
import json
import argparse

from code_names_bot_text_graph.text_disambiguator.text_sense_proposer import TextSenseProposer
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
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
        title = f"{self._current} / {len(self._keys)}: {current_lemma} -- {current_key}"

        text = self._text_dict[current_key]
        token_tags = self._token_tagger.tokenize_tag(text)
        token_senses, compound_indices = self._sense_proposer.propose_senses(token_tags)
        
        if self._disambiguator is not None:
            predicted_senses, _ = self._disambiguator.disambiguate(token_senses, compound_indices)
        else:
            predicted_senses = [None] * len(token_senses)

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
    with open(TEXT_SENSE_LABELS, "w+") as file:
        file.write(json.dumps(sense_labels, sort_keys=True, indent=4, ensure_ascii=False))


def read_sense_inventory():
    with open(SENSE_INVENTORY, "r") as file:
        return json.loads(file.read())


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", type=int, default=0)
    parser.add_argument("-l", action="store_true")
    parser.add_argument("-t", type=str, default=None)
    parser.add_argument('--no-disambiguate', dest='disambiguate', action='store_false')
    parser.set_defaults(disambiguate=True)

    args = parser.parse_args()
    return args.s, args.l, args.t, args.disambiguate


def main():
    start, labels_only, text_id, should_disambiguate = get_args()

    dictionary = read_dictionary()
    sense_labels = read_labels()
    text_dict = read_text_dict()
    sense_inventory_data = read_sense_inventory()

    token_tagger = TokenTagger()
    sense_inventory = SenseInventory(sense_inventory_data)
    sense_proposer = TextSenseProposer(sense_inventory)
    disambiguator = ConsecCompoundTextDisambiguator(dictionary) if should_disambiguate else None

    labeler = TextLabeler(token_tagger, sense_proposer, disambiguator, TextLabelerWindow, text_dict, dictionary, sense_labels, save_labels)

    if text_id is not None:
        keys = [ text_id ]
    elif labels_only == True:
        keys = list(sense_labels.keys())
    elif labels_only == False:
        keys = text_dict.keys()
        keys = list(filter(lambda key: key not in sense_labels, keys))
        random.seed(0)
        random.shuffle(keys)

    labeler.start(keys, start=start)

if __name__ == "__main__":
    main()