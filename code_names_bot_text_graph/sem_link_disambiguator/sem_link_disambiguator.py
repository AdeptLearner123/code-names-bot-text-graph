from abc import ABC, abstractmethod

class SemLinkDisambiguator(ABC):
    @abstractmethod
    def disambiguate(self, sense_id, link_senses, link_type):
        pass