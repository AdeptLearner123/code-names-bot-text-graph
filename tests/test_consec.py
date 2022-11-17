import json

from code_names_bot_text_graph.text_disambiguator.consec_compound_text_disambiguator import ConsecCompoundTextDisambiguator

from config import DICTIONARY
import time

def main():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    """
    token_senses = [
        ("I", []),
        ("have", []),
        ("a", []),
        ("beautiful", ["m_en_gbus0081680.006"]),
        ("dog", ["m_en_gbus0287810.007", "m_en_gbus0287810.012", "m_en_gbus0287810.013", "m_en_gbus0287810.019", "m_en_gbus0287810.020", "m_en_gbus0287810.023"])
    ]
    """

    token_senses = [
        ("The", []),
        ("Amazing", ['The_Amazing_Spider-Man_(film)']),
        ("Spider", ['The_Amazing_Spider-Man_(film)']),
        ("-", ['The_Amazing_Spider-Man_(film)']),
        ("Man", ['The_Amazing_Spider-Man_(film)']),
        ("Annual", [])
    ]

    compound_indices = [
        ("The_Amazing_Spider-Man_(film)", (2, 5)),
        ("The_Amazing_Spider-Man_(film)", (0, 5))
    ]

    disambiguator = ConsecCompoundTextDisambiguator(dictionary, True)
    start = time.time()
    senses = disambiguator.disambiguate(token_senses, compound_indices)
    print("Time", time.time() - start)
    print(senses)


if __name__ == "__main__":
    main()