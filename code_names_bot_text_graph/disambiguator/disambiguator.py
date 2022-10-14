from abc import ABC, abstractmethod

class Disambiguator(ABC):

    def __init__(self, dictionary):
        self._dictionary = dictionary

    def _get_definition(self, sense):
        return self._dictionary[sense]["definition"]

    @abstractmethod
    def disambiguate(self, token_senses):
        pass