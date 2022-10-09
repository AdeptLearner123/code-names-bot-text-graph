import spacy

import yaml
from tqdm import tqdm

from config import DICTIONARY, SENSE_INVENTORY

nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])


def main():
    print("Status:", "reading")
    with open(DICTIONARY, "r") as file:
        dictionary = yaml.safe_load(file)

    print("Status:", "compiling map")
    lemma_senses = dict()
    lemma_lengths = dict()
    for key, entry in tqdm(list(dictionary.items())):
        lemma_forms = [entry["lemma"]] + entry["variants"]
        pos = entry["pos"]
        for lemma_form in lemma_forms:
            lemma_pos = f"{lemma_form}|{pos}"
            if lemma_pos not in lemma_senses:
                lemma_senses[lemma_pos] = []
                lemma_lengths[lemma_pos] = len(nlp(lemma_form))
            lemma_senses[lemma_pos].append(key)

    lines = []
    for lemma_pos in sorted(list(lemma_senses.keys())):
        line = "\t".join([lemma_pos, str(lemma_lengths[lemma_pos]), "|".join(lemma_senses[lemma_pos])])
        lines.append(line)

    print("Status:", "writing")
    with open(SENSE_INVENTORY, "w+") as file:
        file.write("\n".join(lines))


if __name__ == "__main__":
    main()
