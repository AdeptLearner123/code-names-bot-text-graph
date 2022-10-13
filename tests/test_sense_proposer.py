import sys
import json

from code_names_bot_text_graph.sense_proposal.sense_proposer import SenseProposer
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger

from config import SENSE_INVENTORY


def main():
    with open(SENSE_INVENTORY, "r") as file:
        sense_inventory = json.loads(file.read())
    
    token_tagger = TokenTagger()
    sense_proposer = SenseProposer(sense_inventory)

    token_tags = token_tagger.tokenize_tag(sys.argv[1])
    token_senses = sense_proposer.propose_senses(token_tags)

    for token, senses in token_senses:
        print(token, senses)


if __name__ == "__main__":
    main()
