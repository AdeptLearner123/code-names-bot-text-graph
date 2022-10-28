import spacy

class TokenTagger():
    SPACY_POS_TO_TAG = {
        "NOUN": "noun",
        "PROPN": "proper",
        "VERB": "verb",
        "ADJ": "adjective",
        "ADV": "adverb",
    }

    MANUAL_REMOVE_STOP_WORDS = {
        "us" # Don't want "US" as in United States to be classified as a stop word
    }
    
    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self._nlp.Defaults.stop_words -= self.MANUAL_REMOVE_STOP_WORDS

    def _get_token_tag(self, token):
        if token.is_stop:
            return "STOP"

        if token.pos_ in self.SPACY_POS_TO_TAG:
            return self.SPACY_POS_TO_TAG[token.pos_]
        
        return None

    def tokenize_tag(self, text):
        doc = self._nlp(text)

        tokens = [ token.text for token in doc ]
        tags = [ self._get_token_tag(token) for token in doc ]
        return list(zip(tokens, tags))