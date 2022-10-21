from .sem_link_disambiguator import SemLinkDisambiguator

class BaselineSemLinkDisambiguator(SemLinkDisambiguator):
    def disambiguate(self, sense_id, link_senses, link_type):
        if link_senses is None or len(link_senses) == 0:
            return None        
        return link_senses[0]