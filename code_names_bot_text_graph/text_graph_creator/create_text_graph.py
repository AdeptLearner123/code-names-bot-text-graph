from config import DICTIONARY_TEXT_LINKED, DOMAIN_TO_SENSE, CLASS_TO_SENSE, TEXT_SENSES, SENSE_EDGES, LEMMA_SENSE_EDGES, SENSE_INVENTORY
from code_names_bot_text_graph.synonym_disambiguator.synonym_disambiguator import SynonymDisambiguator
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory

import json


def add_sem_link_edges(sense_id, entry, sem_link_to_sense, sense_edges, sem_link_field, sem_link_type):
    for sem_link in entry[sem_link_field]:
        if sem_link not in sem_link_to_sense:
            continue

        sem_link_sense = sem_link_to_sense[sem_link]
        if sem_link_sense is not None:
            sense_edges.append((sense_id, sem_link_sense, sem_link_type, ""))


def add_synonym_edges(sense_id, entry, sense_inventory, synonym_disambiguator, sense_edges):
    pos = entry["pos"]
    for synonym in entry["synonyms"]:
        synonym_senses = sense_inventory.get_senses_from_lemma(synonym, pos)
        synonym_sense = synonym_disambiguator.disambiguate(sense_id, synonym_senses)

        if synonym_sense is not None:
            sense_edges.append((sense_id, synonym_sense, "SYNONYM", ""))


def add_text_edges(sense_id, entry, text_senses, sense_edges):
    text_ids = [entry["definition"]] + entry["texts"]
    for text_id in text_ids:
        if text_id not in text_senses:
            continue
        
        for link_sense in text_senses[text_id]["senses"]:
            start = link_sense["start"]
            length = link_sense["len"]
            sense_edges.append((sense_id, link_sense["sense"], "TEXT", f"{text_id}|{start}|{length}"))


def get_sense_edges(dictionary, sense_inventory, synonym_disambiguator, text_senses, class_to_sense, domain_to_sense):
    sense_edges = []

    for sense_id, entry in dictionary.items():
        add_sem_link_edges(sense_id, entry, class_to_sense, sense_edges, "classes", "CLASS")
        add_sem_link_edges(sense_id, entry, domain_to_sense, sense_edges, "domains", "DOMAIN")
        add_synonym_edges(sense_id, entry, sense_inventory, synonym_disambiguator, sense_edges)
        add_text_edges(sense_id, entry, text_senses, sense_edges)
    
    return sense_edges


def get_lemma_edges(dictionary):
    lemma_sense_edges = []

    for sense_id, entry in dictionary.items():
        lemma = entry["lemma"]
        tokens = lemma.replace("-", " ").split(" ")

        if len(tokens) == 1:
            lemma_sense_edges.append((lemma.upper(), sense_id, "SENSE", str(entry["meta"]["is_primary"])))
        else:
            for token in tokens:
                lemma_sense_edges.append((token.upper(), sense_id, "COMPOUND", str(len(tokens))))

    return lemma_sense_edges


def main():
    with open(DICTIONARY_TEXT_LINKED, "r") as file:
        dictionary = json.loads(file.read())
    
    with open(DOMAIN_TO_SENSE, "r") as file:
        domain_to_sense = json.loads(file.read())
    
    with open(CLASS_TO_SENSE, "r") as file:
        class_to_sense = json.loads(file.read())

    with open(TEXT_SENSES, "r") as file:
        text_senses = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())
        sense_inventory = SenseInventory(sense_inventory_data)

    synonym_disambiguator = SynonymDisambiguator(dictionary)

    sense_edges = get_sense_edges(dictionary, sense_inventory, synonym_disambiguator, text_senses, class_to_sense, domain_to_sense)
    lemma_sense_edges = get_lemma_edges(dictionary)

    with open(SENSE_EDGES, "w+") as file:
        lines = [ "\t".join(edge) for edge in sense_edges ]
        file.write("\n".join(lines))

    with open(LEMMA_SENSE_EDGES, "w+") as file:
        lines = [ "\t".join(edge) for edge in lemma_sense_edges ]
        file.write("\n".join(lines))


if __name__ == "__main__":
    main()