import sys
import spacy

nlp = spacy.load("en_core_web_sm")

def main():
    doc = nlp(sys.argv[1])
    for token in doc:
        print(token.text, token.pos_, token.lemma_)    


if __name__ == "__main__":
    main()