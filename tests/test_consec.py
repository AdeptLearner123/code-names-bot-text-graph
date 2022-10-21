import json

from code_names_bot_text_graph.text_disambiguator.consec_text_disambiguator import ConsecTextDisambiguator

from config import DICTIONARY
import time

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

    """
    token_senses = [
        ("relating", ['m_en_gbus0859220.013', 'm_en_gbus0859220.015', 'm_en_gbus0859220.016', 'm_en_gbus0859220.018', 'm_en_gbus0859220.020', 'm_en_gbus0859220.007']),
        ("to", []),
        ("or", []),
        ("denoting", []),
        ("(", []),
        ("fictional", []),
        ("or", []),
        ("hypothetical", []),
        (")", []),
        ("space", []),
        ("travel", []),
        ("by", []),
        ("means", []),
        ("of", []),
        ("distorting", []),
        ("space", []),
        ("-", []),
        ("time", [])
    ]
    """

    disambiguator = ConsecTextDisambiguator(dictionary, True)
    start = time.time()
    senses = disambiguator.disambiguate(token_senses)
    print("Time", time.time() - start)
    print(senses)


if __name__ == "__main__":
    main()