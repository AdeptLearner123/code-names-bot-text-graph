import json
from collections import defaultdict
from tqdm import tqdm

from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from config import DICTIONARY, DOMAIN_TO_SENSE, CLASS_TO_SENSE


POS_ORDER = ["proper", "noun", "adjective", "verb"]

def get_all_sem_links(dictionary):
    domains = set()
    classes = set()
    for entry in dictionary.values():
        domains.update(entry["domains"])
        classes.update(entry["classes"])
    return domains, classes


def get_sense_possibilities(dictionary, domains, classes):
    domain_senses = dict()
    class_senses = dict()

    for domain in domains:
        domain_senses[domain] = []
    for class_lemma in classes:
        class_senses[class_lemma] = []

    for sense_id, entry in tqdm(dictionary.items()):
        if entry["pos"] not in POS_ORDER:
            continue

        lemma = entry["lemma"]
        lemma_variants = set([ lemma.lower() ] + [ variant.lower() for variant in entry["variants"] ] + [ derivative.lower() for derivative in entry["derivatives"] ])

        for domain in domains:
            if domain.lower() in lemma_variants:
                domain_senses[domain].append(sense_id)
        for class_lemma in classes:
            if class_lemma.lower() in lemma_variants:
                class_senses[class_lemma].append(sense_id)
    
    return domain_senses, class_senses


def select_sense(dictionary, sem_link, senses, is_domain):
    key = "domains" if is_domain else "classes"
    candidates = []
    
    for sense in senses:
        entry = dictionary[sense]

        if entry["source"] != "OX":
            continue

        metadata = entry["meta"]
        if "is_subsense" in metadata and metadata["is_subsense"]:
            continue

        direct_link = sem_link in entry[key]
        candidates.append((sense, (not direct_link, POS_ORDER.index(entry["pos"]), metadata["sense_idx"], metadata["sentence_count"])))
    
    if sem_link == "gaming":
        print(candidates)
        print(sorted(candidates))
    candidates = sorted(candidates, key=lambda candidate: candidate[1])
    if len(candidates) > 0:
        sense, _ = candidates[0]
        return sense

    return None


def assign_senses(dictionary, sem_link_senses, is_domain):
    sem_link_to_sense = dict()
    for sem_link, senses in sem_link_senses.items():
        sem_link_to_sense[sem_link] = select_sense(dictionary, sem_link, senses, is_domain)
    return sem_link_to_sense


def main():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    domains, classes = get_all_sem_links(dictionary)
    domain_senses, class_senses = get_sense_possibilities(dictionary, domains, classes)

    domain_to_sense = assign_senses(dictionary, domain_senses, True)
    class_to_sense = assign_senses(dictionary, class_senses, False)

    print("Unassigned domains", list(domain_to_sense.values()).count(None), "/", len(domain_to_sense))
    print("Unassigned classes", list(class_to_sense.values()).count(None), "/", len(class_to_sense))

    with open(DOMAIN_TO_SENSE, "w+") as file:
        file.write(json.dumps(domain_to_sense, sort_keys=True, indent=4))
    
    with open(CLASS_TO_SENSE, "w+") as file:
        file.write(json.dumps(class_to_sense, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()