from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.text_disambiguator.text_sense_proposer import TextSenseProposer
from code_names_bot_text_graph.text_disambiguator.consec_compound_text_disambiguator import ConsecCompoundTextDisambiguator
from config import TEXT_LIST, DICTIONARY, SENSE_INVENTORY, TEXT_SENSE_BATCHES

import json
import os
from tqdm import tqdm


SAVE_INTERVAL = 1000

def disambiguate(token_tagger, sense_proposer, disambiguator, text):
    doc = token_tagger.get_doc(text)
    token_tags = token_tagger.tokenize_tag_doc(doc)
    token_senses, compound_indices = sense_proposer.propose_senses(token_tags)
    senses, join_indices = disambiguator.disambiguate(token_senses, compound_indices)

    sense_indices = []
    for i, sense in enumerate(senses):
        if sense is None:
            sense_indices.append(None)
        else:
            sense_indices.append((sense, (i, i + 1)))
    
    for start, end in join_indices:
        sense_indices[start] = (senses[start], (start, end))
        sense_indices[start + 1:end] = [None] * (end - start - 1)

    sense_indices = [ item for item in sense_indices if item is not None ]

    sense_char_idxs = []
    for sense, (start, end) in sense_indices:
        start_idx = doc[start].idx
        length = len(doc[start:end].text)

        sense_char_idxs.append({
            "sense": sense,
            "start": start_idx,
            "len": length
        })

    return sense_char_idxs


def save(batch_id, batch_text_senses):
    print("Saving", len(batch_text_senses))
    filename = f"batch_{batch_id}.json"
    path = os.path.join(TEXT_SENSE_BATCHES, filename)

    if os.path.isfile(path):
        raise "Batch file path already exists: " + path

    with open(path, "w+") as file:
        file.write(json.dumps(batch_text_senses, sort_keys=True, indent=4, ensure_ascii=False))


def get_disambiguated_text_ids():
    text_ids = set()
    for filename in os.listdir(TEXT_SENSE_BATCHES):
        if filename.endswith(".json"):
            with open(os.path.join(TEXT_SENSE_BATCHES, filename), "r") as file:
                file_json = json.loads(file.read())
                text_ids.update(file_json.keys())
    return text_ids


def main():
    with open(TEXT_LIST, "r") as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        text_dict = { line[0]: line[1] for line in lines }
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())

    token_tagger = TokenTagger()
    sense_inventory = SenseInventory(sense_inventory_data)
    sense_proposer = TextSenseProposer(sense_inventory)
    disambiguator = ConsecCompoundTextDisambiguator(dictionary)

    disambiguated_text_ids = get_disambiguated_text_ids()
    #missing_text_ids = set(text_dict.keys()).difference(disambiguated_text_ids)
    missing_text_ids = set(["m_en_gbus1126880.005_def", "The_Starry_Night_text_1"])
    print("Text ids:", len(missing_text_ids), "/", len(text_dict))

    batch_text_senses = dict()
    batch_id = len(disambiguated_text_ids)
    for i, text_id in tqdm(list(enumerate(missing_text_ids))):
        text = text_dict[text_id]
        batch_text_senses[text_id] = {
            "text": text,
            "senses": disambiguate(token_tagger, sense_proposer, disambiguator, text_dict[text_id])
        }

        if (i + 1) % SAVE_INTERVAL == 0:
            save(batch_id, batch_text_senses)
            batch_text_senses = dict()
            batch_id += SAVE_INTERVAL
    save(batch_id, batch_text_senses)


if __name__ == "__main__":
    main()