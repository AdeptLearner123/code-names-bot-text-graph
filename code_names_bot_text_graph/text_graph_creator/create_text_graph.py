from config import DICTIONARY, DOMAIN_TO_SENSE, CLASS_TO_SENSE
from code_names_bot_text_graph.synonym_disambiguator.synonym_disambiguator import SynonymDisambiguator

import json

def main():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())
    
    with open(DOMAIN_TO_SENSE, "r") as file:
        domain_to_sense = json.loads(file.read())
    
    with open(CLASS_TO_SENSE, "r") as file:
        class_to_sense = json.loads(file.read())

    synonym_disambiguator = SynonymDisambiguator(dictionary)

    for sense_id, entry in dictionary.items():
        


if __name__ == "__main__":
    main()