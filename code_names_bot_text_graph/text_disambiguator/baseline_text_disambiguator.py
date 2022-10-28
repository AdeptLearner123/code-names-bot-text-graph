from .text_disambiguator import TextDisambiguator

class BaselineTextDisambiguator(TextDisambiguator):
    def disambiguate(self, token_senses, compound_indices):
        predicted_senses = []

        for _, senses in token_senses:
            if len(senses) == 0:
                predicted_senses.append(None)
            else:
                predicted_senses.append(senses[0])
        return predicted_senses