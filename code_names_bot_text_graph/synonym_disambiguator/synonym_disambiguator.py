class SynonymDisambiguator:
    def __init__(self, dictionary):
        self._dictionary = dictionary
    
    def _get_synonyms(self, sense_id):
        return self._dictionary[sense_id]["synonyms"]
    
    def _get_lemma(self, sense_id):
        return self._dictionary[sense_id]["lemma"]

    def disambiguate(self, sense_id, synonym_senses):
        # If link is synonym, find sense that has this lemma as a synonym
        lemma = self._get_lemma(sense_id)

        for synonym_sense in synonym_senses:
            if lemma in self._get_synonyms(synonym_sense):
                return synonym_sense
        return None