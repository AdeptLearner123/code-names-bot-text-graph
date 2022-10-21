from .semantic_disambiguator import SemanticDisambiguator

class SynonymDisambiguator(SemanticDisambiguator):

    def __init__(self, dictionary):
        self._dictionary = dictionary

    def _get_definition(self, sense):
        return self._dictionary[sense]["definition"]

    def _get_lemma(self, sense_id):
        return self._dictionary[sense_id]["lemma"]
    
    def _get_synonyms(self, sense_id):
        return self._dictionary[sense_id]["synonyms"]

    def disambiguate(self, sense_id, synonym_senses):
        if synonym_senses is None or len(synonym_senses) == 0:
            return None        
    
        lemma = self._get_lemma(sense_id)

        for synonym_sense in synonym_senses:
            if lemma in self._get_synonyms(synonym_sense):
                return synonym_sense
        return None