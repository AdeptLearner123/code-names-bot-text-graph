class SenseInventory:
    def __init__(self, sense_inventory_data):
        self._key_to_senses = dict()
        
        for lemma_pos, entry in sense_inventory_data.items():
            lemma, pos = lemma_pos.split("|")
            lemma_tokens = tuple(entry["tokens"])
            senses = entry["senses"]

            keys = [ (lemma, None), (lemma, pos), (lemma_tokens, None), (lemma_tokens, pos)]
            
            for key in keys:
                if key not in self._key_to_senses:
                    self._key_to_senses[key] = []
                self._key_to_senses[key] += senses
    
    def get_senses_from_tokens(self, tokens, pos=None):
        key = (tuple(tokens), pos)
        return self._key_to_senses[key] if key in self._key_to_senses else []

    def get_senses_from_lemma(self, lemma, pos=None):
        key = (lemma, pos)
        return self._key_to_senses[key] if key in self._key_to_senses else []