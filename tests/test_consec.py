import json

from code_names_bot_text_graph.disambiguator.consec_disambiguator import ConsecDisambiguator

from config import DICTIONARY

def main():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    token_senses = [
        ("I", []),
        ("have", []),
        ("a", []),
        ("beautiful", ["m_en_gbus0081680.006"]),
        ("dog", ["m_en_gbus0287810.007", "m_en_gbus0287810.012", "m_en_gbus0287810.013", "m_en_gbus0287810.019", "m_en_gbus0287810.020", "m_en_gbus0287810.023"])
    ]
    disambiguator = ConsecDisambiguator(dictionary)
    senses = disambiguator.disambiguate(token_senses)
    print(senses)


if __name__ == "__main__":
    main()