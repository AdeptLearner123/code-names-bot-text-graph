from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.sense_inventory.sense_inventory import SenseInventory
from code_names_bot_text_graph.text_disambiguator.text_sense_proposer import TextSenseProposer
from code_names_bot_text_graph.text_disambiguator.consec_compound_text_disambiguator import ConsecCompoundTextDisambiguator
from config import TEXT_LIST, DICTIONARY, SENSE_INVENTORY, TEXT_SENSES

import json
from tqdm import tqdm


SAVE_INTERVAL = 5 #50

def disambiguate(token_tagger, sense_proposer, disambiguator, text):
    doc = token_tagger.get_doc(text)
    token_tags = token_tagger.tokenize_tag_doc(doc)
    token_senses, compound_indices = sense_proposer.propose_senses(token_tags)
    senses = disambiguator.disambiguate(token_senses, compound_indices)

    sense_char_idxs = []
    for sense, token in zip(senses, doc):
        if sense is not None:
            sense_char_idxs.append({
                "sense": sense,
                "start": token.idx,
                "len": len(token)
            })
    
    return sense_char_idxs


def save(text_senses):
    print("Saving", len(text_senses))
    with open(TEXT_SENSES, "w") as file:
        file.write(json.dumps(text_senses, sort_keys=True, indent=4, ensure_ascii=False))


def main():
    with open(TEXT_LIST, "r") as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        text_dict = { line[0]: line[1] for line in lines }
    
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory_data = json.loads(file.read())

    with open(TEXT_SENSES, "r") as file:
        text_senses = json.loads(file.read())

    token_tagger = TokenTagger()
    sense_inventory = SenseInventory(sense_inventory_data)
    sense_proposer = TextSenseProposer(sense_inventory)
    disambiguator = ConsecCompoundTextDisambiguator(dictionary)

    missing_text_ids = set(text_dict.keys()).difference(text_senses.keys())
    print("Text ids:", len(missing_text_ids), "/", len(text_dict))

    for i, text_id in tqdm(list(enumerate(missing_text_ids))):
        text = text_dict[text_id]
        text_senses[text_id] = {
            "text": text,
            "senses": disambiguate(token_tagger, sense_proposer, disambiguator, text_dict[text_id])
        }

        if i > 0 and i % SAVE_INTERVAL == 0:
            save(text_senses)
    save(text_senses)


if __name__ == "__main__":
    main()