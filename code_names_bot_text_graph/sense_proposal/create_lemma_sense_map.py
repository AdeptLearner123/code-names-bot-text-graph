import yaml
from collections import defaultdict

from config import DICTIONARY, LEMMA_SENSE_MAP


def main():
    print("Status:", "reading")
    with open(DICTIONARY, "r") as file:
        dictionary = yaml.safe_load(file)

    print("Status:", "compiling map")
    lemma_sense_map = defaultdict(lambda: [])
    for key, entry in dictionary.items():
        lemma_forms = [entry["lemma"]] + entry["variants"]
        pos = entry["pos"]
        for lemma_form in lemma_forms:
            lemma_pos = f"{lemma_form}|{pos}"
            lemma_sense_map[lemma_pos].append(key)
    lemma_sense_map = dict(lemma_sense_map)

    print("Status:", "writing")
    with open(LEMMA_SENSE_MAP, "w+") as file:
        yaml.dump(lemma_sense_map, file, default_flow_style=None, sort_keys=True, allow_unicode=True)


if __name__ == "__main__":
    main()
