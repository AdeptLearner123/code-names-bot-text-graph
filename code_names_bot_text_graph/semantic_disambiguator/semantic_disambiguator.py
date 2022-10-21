from abc import ABC, abstractmethod

class SemanticDisambiguator(ABC):

    def __init__(self, dictionary):
        self._dictionary = dictionary

    def _get_definition(self, sense):
        return self._dictionary[sense]["definition"]

    @abstractmethod
    def disambiguate(self, sense_id, synonym_senses):
        pass