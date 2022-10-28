from collections import defaultdict

class SenseInventory:
    def __init__(self, sense_inventory_data):
        self._key_to_senses = defaultdict(lambda: [])
        
        for lemma_pos, entry in sense_inventory_data.items():
            lemma, pos = lemma_pos.split("|")
            lemma_tokens = tuple(entry["tokens"])
            senses = entry["senses"]

            keys = [ (lemma, None), (lemma, pos), (lemma_tokens, None), (lemma_tokens, pos), (lemma.lower(), "ignore-case")]
            
            for key in keys:
                if key not in self._key_to_senses:
                    self._key_to_senses[key] = []
                self._key_to_senses[key] += senses
        
    def get_senses_from_tokens(self, tokens, pos=None):
        key = (tuple(tokens), pos)
        return self._key_to_senses[key]

    def get_senses_from_lemma(self, lemma, pos=None):
        key = (lemma, pos)
        return self._key_to_senses[key]
    
    def get_senses_from_lemma_ignore_case(self, lemma):
        key = (lemma.lower(), "ignore-case")
        return self._key_to_senses[key]