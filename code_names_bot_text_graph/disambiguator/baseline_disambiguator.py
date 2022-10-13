from .disambiguator import Disambiguator

class BaselineDisambiguator(Disambiguator):
    def disambiguate(tokens, sense_definitions_list):
        senses = []

        for sense_definitions in sense_definitions_list:
            if len(sense_definitions) == 0:
                senses.append(None)
            else:
                first_sense, _ = sense_definitions[0]
                senses.append(first_sense)
        return senses