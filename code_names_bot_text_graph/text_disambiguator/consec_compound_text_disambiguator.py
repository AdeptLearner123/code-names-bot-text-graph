from .consec_text_disambiguator import ConsecTextDisambiguator

class ConsecCompoundTextDisambiguator(ConsecTextDisambiguator):
    def disambiguate(self, token_senses, compound_indices):
        senses = super().disambiguate(token_senses, compound_indices)

        for sense, (start, end) in compound_indices:
            if sense in senses[start:end]:
                senses[start:end] = [sense] * (end - start)

        return senses
    
    def batch_disambiguate(self, token_senses_compound_indices_list):
        compound_indices_list = [ compound_indices for _, compound_indices in token_senses_compound_indices_list]
        senses_list = super().batch_disambiguate(token_senses_compound_indices_list)

        print("Text disambiguator", senses_list)
        print(compound_indices_list)
        for senses, compound_indices in zip(senses_list, compound_indices_list):
            print("Iter", senses, compound_indices)
            for sense, (start, end) in compound_indices:
                if sense in senses[start:end]:
                    senses[start:end] = [sense] * (end - start)
        
        return senses_list