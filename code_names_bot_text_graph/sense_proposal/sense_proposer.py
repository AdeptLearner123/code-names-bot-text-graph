import spacy
import yaml
from tqdm import tqdm

from config import SENSE_INVENTORY


class SenseProposer:
    SPACY_POS_CONVERTER = {
        "NOUN": "noun",
        "PROPN": "proper",
        "ADJ": "adjective",
        "ADV": "adverb",
    }

    def __init__(self):
        nlp = spacy.load("en_core_web_sm")
        self._nlp = nlp

        print("Creating sense inventory")
        with open(SENSE_INVENTORY, "r") as file:
            lines = file.read().splitlines()
            lines = [line.split("\t") for line in lines]
            lemma_senses = {line[0]: line[2].split("|") for line in lines}
            lemma_lengths = {line[0]: int(line[1]) for line in lines}

        print("Sorting lemmas by length")
        self._construct_lemma_lookup(lemma_senses, lemma_lengths)
        print("Finished init")

    def _construct_lemma_lookup(self, lemma_senses, lemma_lengths):
        self._lemmas_by_length = dict()
        for lemma_pos in lemma_senses:
            [lemma, pos] = lemma_pos.split("|")

            length = lemma_lengths[lemma_pos]
            if length not in self._lemmas_by_length:
                self._lemmas_by_length[length] = dict()

            if lemma == "Africa":
                print("Lemma is Africa")
            key = (lemma, pos) if length == 1 else lemma
            if key not in self._lemmas_by_length:
                if lemma == "Africa":
                    print("Storing key", key)
                self._lemmas_by_length[length][key] = []
            self._lemmas_by_length[length][key] += lemma_senses[lemma_pos]

    def _assign_multi_word_possibilities(
        self, doc, token_senses, lemma_to_senses, length
    ):
        for i in range(len(doc) - length + 1):
            span = doc[i : i + length].text
            print("Span", span, span in lemma_to_senses)
            if span in lemma_to_senses:
                for _, senses in token_senses[i : i + length]:
                    senses += lemma_to_senses[span]

    def _assign_single_word_possibilities(self, doc, token_senses, lemma_to_senses):
        for i, token in enumerate(doc):
            if token.pos_ not in self.SPACY_POS_CONVERTER or token.is_stop:
                continue

            key = (token.text, self.SPACY_POS_CONVERTER[token.pos_])
            print("Key", key, key in lemma_to_senses, token.pos_)
            if key not in lemma_to_senses:
                continue

            _, senses = token_senses[i]
            senses += lemma_to_senses[key]

    def propose_senses(self, text):
        doc = self._nlp(text)
        token_senses = [(token.text, []) for token in doc]

        for length in range(2, 5):
            self._assign_multi_word_possibilities(
                doc, token_senses, self._lemmas_by_length[length], length
            )
        self._assign_single_word_possibilities(
            doc, token_senses, self._lemmas_by_length[1]
        )

        return token_senses
