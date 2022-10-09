import sys

from code_names_bot_text_graph.sense_proposal.sense_proposer import SenseProposer

def main():
    sense_proposer = SenseProposer()
    token_senses = sense_proposer.propose_senses(sys.argv[1])

    for token, senses in token_senses:
        print(token, senses)


if __name__ == "__main__":
    main()