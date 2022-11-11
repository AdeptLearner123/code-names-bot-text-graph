from .consec_text_disambiguator import ConsecTextDisambiguator

class ConsecCompoundTextDisambiguator(ConsecTextDisambiguator):
    def disambiguate(self, token_senses, compound_indices):
        senses, _ = super().disambiguate(token_senses, compound_indices)

        join_indices = []
        for sense, (start, end) in compound_indices:
            if sense in senses[start:end]:
                senses[start:end] = [sense] * (end - start)
                join_indices.append((start, end))

        return senses, join_indices
    
    def batch_disambiguate(self, token_senses_compound_indices_list):
        compound_indices_list = [ compound_indices for _, compound_indices in token_senses_compound_indices_list]
        senses_list = super().batch_disambiguate(token_senses_compound_indices_list)

        join_indices = []
        for senses, compound_indices in zip(senses_list, compound_indices_list):
            for sense, (start, end) in compound_indices:
                if sense in senses[start:end]:
                    senses[start:end] = [sense] * (end - start)
                    join_indices.append((start, end))
        
        return senses_list, join_indices