import torch
import numpy as np

from .disambiguator import Disambiguator
from config import CONSEC_MODEL_STATE
from code_names_bot_text_graph.consec.tokenizer import ConsecTokenizer
from code_names_bot_text_graph.consec.sense_extractor import SenseExtractor

class ConsecDisambiguator(Disambiguator):
    def __init__(self, dictionary, debug_mode=False):
        super().__init__(dictionary)

        self._debug_mode = debug_mode
        state_dict = torch.load(CONSEC_MODEL_STATE)
        self._sense_extractor = SenseExtractor()
        self._sense_extractor.load_state_dict(state_dict)
        
        self._tokenizer = ConsecTokenizer()
    
    def _disambiguate_token(self, tokens, target_idx, candidate_senses, context_senses):
        candidate_definitions = [ self._get_definition(sense) for sense in candidate_senses ]
        context_definitions = [ (i, self._get_definition(sense)) for i, sense in context_senses ]
        #context_definitions = []

        tokenizer_result = self._tokenizer.tokenize(tokens, target_idx, candidate_definitions, context_definitions)
        probs = self._sense_extractor.extract(*tokenizer_result)

        if self._debug_mode:
            sense_idxs = torch.tensor(probs).argsort(descending=True)
            for sense_idx in sense_idxs:
                print(f"{candidate_senses[sense_idx]}:  {probs[sense_idx]} --- {candidate_definitions[sense_idx]}")

        sense_idx = torch.argmax(torch.tensor(probs))
        return candidate_senses[sense_idx]

    def disambiguate(self, token_senses):
        tokens = [ token for token, _ in token_senses ]
        token_polysemy = [ len(senses) for _, senses in token_senses ]
        disambiguation_order = torch.tensor(token_polysemy).argsort()
        disambiguated_senses = [None] * len(token_senses)

        for idx in disambiguation_order:
            _, candidate_senses = token_senses[idx]
            
            if len(candidate_senses) == 0:
                continue
            
            if len(candidate_senses) == 1:
                disambiguated_senses[idx] = candidate_senses[0]
                continue

            context_senses = [ (i, sense) for i, sense in enumerate(disambiguated_senses) if sense is not None ]
            disambiguated_senses[idx] = self._disambiguate_token(tokens, idx, candidate_senses, context_senses)

        return disambiguated_senses