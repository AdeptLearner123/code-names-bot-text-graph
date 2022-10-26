from .sem_link_disambiguator import SemLinkDisambiguator

class DictSemLinkDisambiguator(SemLinkDisambiguator):
    def __init__(self, dictionary):
        self._dictionary = dictionary
    
    def _get_synonyms(self, sense_id):
        return self._dictionary[sense_id]["synonyms"]
    
    def _disambiguate_synonym(self, sense_id, link_senses):
        # If link is synonym, find sense that has this lemma as a synonym
        lemma = self._get_lemma(sense_id)

        for synonym_sense in link_senses:
            if lemma in self._get_synonyms(synonym_sense):
                return synonym_sense
        return None

    def _disambiguate_domain(self, sense_id, link_senses):
        for domain_sense in link_senses:
            if self._dictionary[domain_sense]["domains"]

    def disambiguate(self, sense_id, link_senses, link_type):
        