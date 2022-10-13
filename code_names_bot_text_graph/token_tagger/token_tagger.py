import spacy

class TokenTagger():
    SPACY_POS_TO_TAG = {
        "NOUN": "noun",
        "PROPN": "proper",
        "VERB": "verb",
        "ADJ": "adjective",
        "ADV": "adverb",
    }
    
    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

    def _get_token_tag(self, token):
        if token.is_stop:
            return None

        if token.pos_ in self.SPACY_POS_TO_TAG:
            return self.SPACY_POS_TO_TAG[token.pos_]
        
        return None

    def tokenize_tag(self, text):
        doc = self._nlp(text)

        tokens = [ token.text for token in doc ]
        tags = [ self._get_token_tag(token) for token in doc ]
        return list(zip(tokens, tags))