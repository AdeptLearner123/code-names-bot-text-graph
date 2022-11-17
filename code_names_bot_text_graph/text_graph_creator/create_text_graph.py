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
            sense_edges.append((sense_id, link_sense["sense"], "TEXT", f"{text_id}:{start}:{length}"))


def get_sense_edges(dictionary, sense_inventory, synonym_disambiguator, text_senses, class_to_sense, domain_to_sense):
    sense_edges = []

    for sense_id, entry in dictionary.items():
        add_sem_link_edges(sense_id, entry, class_to_sense, sense_edges, "classes", "CLASS")
        add_sem_link_edges(sense_id, entry, domain_to_sense, sense_edges, "domains", "DOMAIN")
        add_synonym_edges(sense_id, entry, sense_inventory, synonym_disambiguator, sense_edges)
        add_text_edges(sense_id, entry, text_senses, sense_edges)
    
    return sense_edges


def tokenize(lemma):
    return lemma.replace("-", " ").split(" ")


def get_compound_tokens(lemma):
    tokens = tokenize(lemma)

    compound_tokens = []

    if len(tokens) > 1:
        for token in tokens:
            compound_tokens.append(token.upper())
    
    if len(tokens) > 2:
        # Add adjacent tokens, so that "LOCH NESS" is a comopund component of "LOCH NESS MONSTER"
        for i in range(len(tokens) - 1):
            token_pair = (tokens[i], tokens[i + 1])
            separator = " " if " ".join(token_pair) in lemma else "-"
            compound_tokens.append(separator.join(token_pair).upper())
    
    return compound_tokens


def get_lemma_edges(dictionary):
    lemma_sense_edges = []

    for sense_id, entry in dictionary.items():
        lemma = entry["lemma"]
        lemma_sense_edges.append((lemma.upper(), sense_id))
        
        variants = [ variant for variant in entry["variants"] if len(tokenize(variant)) == 1]

        if entry["pos"] == "proper":
            # For Proper nouns, individual tokens count as variants too.
            # Ex: "Jeff" for "Jeff Bezos" or "Yaris" for "Toyota Yaris" or "Loch Ness" for "Loch Ness monster"
            variants += get_compound_tokens(lemma)

        for variant in variants:
            lemma_sense_edges.append((variant.upper(), sense_id))

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