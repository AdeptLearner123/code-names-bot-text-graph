from .consec_text_disambiguator import ConsecTextDisambiguator

class ConsecCompoundTextDisambiguator(ConsecTextDisambiguator):
    def disambiguate(self, token_senses, compound_indices):
        senses = super().disambiguate(token_senses, compound_indices)

        for sense, (start, end) in compound_indices:
            if sense in senses[start:end]:
                senses[start:end] = [sense] * (end - start)

        return senses