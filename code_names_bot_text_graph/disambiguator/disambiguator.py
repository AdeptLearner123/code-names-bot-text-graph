from abc import ABC, abstractmethod

class Disambiguator(ABC):

    @abstractmethod
    def disambiguate(tokens, sense_definitions):
        pass