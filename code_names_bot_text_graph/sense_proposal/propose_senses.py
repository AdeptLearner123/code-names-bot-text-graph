from tqdm import tqdm
import json

from config import SENSE_PROPOSALS, TEXT_LIST
from code_names_bot_text_graph.sense_proposal.sense_proposer import SenseProposer

def main():
    print("Status:", "reading")
    with open(TEXT_LIST, "r") as file:
        lines = file.read().splitlines()
        lines = [ line.split("\t") for line in lines ]
        for line in lines:
            if len(line) < 2:
                print("Missing", line)
        text_dict = { line[0]: line[1] for line in lines }
    
    print("Status:", "proposing senses")
    sense_proposer = SenseProposer()
    sense_proposals = dict()
    for key, text in tqdm(text_dict.items()):
        token_senses = sense_proposer.propose_senses(text)
        sense_proposals[key] = [ { "token": token, "senses": senses } for token, senses in token_senses ]
    
    print("Status", "dumping")
    with open(SENSE_PROPOSALS, "w+") as file:
        file.write(json.dumps(sense_proposals, sort_keys=True, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()