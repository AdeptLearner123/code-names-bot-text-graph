from .consec_text_disambiguator import ConsecTextDisambiguator

class ConsecCompoundTextDisambiguator(ConsecTextDisambiguator):
    def disambiguate(self, token_senses, compound_indices):
        token_senses = super().disambiguate(token_senses, compound_indices)
        tokens = [ token for token, _ in token_senses ]
        senses = [ sense for _, sense in token_senses]

        for sense, (start, end) in compound_indices:
            if sense in senses[start:end]:
                senses[start:end] = sense

        token_senses = zip(tokens, senses)
        return token_senses