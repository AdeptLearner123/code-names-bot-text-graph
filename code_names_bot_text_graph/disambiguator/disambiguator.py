from abc import ABC, abstractmethod

class Disambiguator(ABC):

    def __init__(self, dictionary):
        self._dictionary = dictionary

    @abstractmethod
    def disambiguate(self, token_senses):
        pass