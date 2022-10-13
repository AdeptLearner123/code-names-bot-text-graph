import json
from tqdm import tqdm

from config import DICTIONARY, SENSE_INVENTORY
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger

def main():
    print("Status:", "reading")
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    print("Status:", "compiling map")
    token_tagger = TokenTagger()
    lemma_senses = dict()
    for sense_id, entry in tqdm(list(dictionary.items())):
        lemma_forms = [entry["lemma"]] + entry["variants"]
        pos = entry["pos"]
        for lemma_form in lemma_forms:
            lemma_tokens = [ token for token, _ in token_tagger.tokenize_tag(lemma_form) ]
            # Only match by pos if lemma is single token
            lemma_key = f"{lemma_tokens[0]}|{pos}" if len(lemma_tokens) == 1 else ' '.join(lemma_tokens)
            if lemma_key not in lemma_senses:
                lemma_senses[lemma_key] = []
            lemma_senses[lemma_key].append(sense_id)

    print("Status:", "writing")
    with open(SENSE_INVENTORY, "w+") as file:
        file.write(json.dumps(lemma_senses, sort_keys=True, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()
