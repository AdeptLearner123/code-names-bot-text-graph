from .semantic_disambiguator import SemanticDisambiguator

class BaselineSynonymDisambiguator(SemanticDisambiguator):
    def disambiguate(self, sense_id, synonym_senses):
        if synonym_senses is None or len(synonym_senses) == 0:
            return None        
        return synonym_senses[0]