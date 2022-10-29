import json
from config import TEXT_SENSE_LABELS, TEXT_LIST

from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger

def main():
    with open(TEXT_LIST) as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        text_dict = { line[0]: line[1] for line in lines }

    with open(TEXT_SENSE_LABELS, "r") as file:
        labels = json.loads(file.read())

    token_tagger = TokenTagger()

    for text_id, senses in labels.items():
        token_tags = token_tagger.tokenize_tag(text_dict[text_id])
        for i, (_, tag) in enumerate(token_tags):
            if tag is None:
                senses[i] = None
        labels[text_id] = senses
    
    with open(TEXT_SENSE_LABELS, "w") as file:
        file.write(json.dumps(labels, sort_keys=True, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()