import yaml
from tqdm import tqdm

from config import TEXT_LIST, DICTIONARY_TEXT_LINKED, DICTIONARY


def main():
    print("Status:", "reading")
    with open(DICTIONARY, "r") as file:
        dictionary = yaml.safe_load(file)

    print("Status:", "Extracting and linking")
    text_dict = dict()
    for key in tqdm(dictionary):
        def_key = f"{key}_def"
        text_dict[def_key] = dictionary[key]["definition"]
        dictionary[key]["definition"] = def_key

        for i, text in enumerate(dictionary[key]["texts"]):
            text_key = f"{key}_text_{i}"
            text_dict[text_key] = text
            dictionary[key]["texts"][i] = text_key

    print("Status:", "Dumping text list")
    lines = [f"{key}\t{text}" for key, text in text_dict.items()]
    with open(TEXT_LIST, "w+") as file:
        file.write("\n".join(lines))

    print("Status:", "Dumping text linked dictionary")
    with open(DICTIONARY_TEXT_LINKED, "w+") as file:
        yaml.dump(dictionary, file)


if __name__ == "__main__":
    main()
