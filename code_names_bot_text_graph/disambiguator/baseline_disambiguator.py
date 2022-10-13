from .disambiguator import Disambiguator

class BaselineDisambiguator(Disambiguator):
    def disambiguate(self, token_senses):
        predicted_senses = []

        for _, senses in token_senses:
            if len(senses) == 0:
                predicted_senses.append(None)
            else:
                predicted_senses.append(senses[0])
        return predicted_senses