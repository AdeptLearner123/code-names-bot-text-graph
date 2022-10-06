import yaml
from collections import defaultdict

from config import DICTIONARY, LEMMA_SENSE_MAP


def main():
    print("Status:", "reading")
    with open(DICTIONARY, "r") as file:
        dictionary = yaml.safe_load(file)

    lemma_sense_map = defaultdict(lambda: [])

    print("Status:", "compiling map")
    for entry in dictionary.values():
        lemma_forms = [entry["lemma"]] + entry["variants"]
        pos = entry["pos"]
        for lemma_form in lemma_forms:
            lemma_pos = (lemma_form, pos)
            lemma_sense_map[lemma_pos].append(lemma_form)

    print("Status:", "writing")
    with open(LEMMA_SENSE_MAP, "w+") as file:
        yaml.dump(lemma_sense_map, file)


if __name__ == "__main__":
    main()
