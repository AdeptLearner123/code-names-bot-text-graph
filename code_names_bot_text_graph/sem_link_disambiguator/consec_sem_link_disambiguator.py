import torch

from config import CONSEC_MODEL_STATE
from .sem_link_disambiguator import SemLinkDisambiguator
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.consec.sense_extractor import SenseExtractor
from code_names_bot_text_graph.consec.tokenizer import ConsecTokenizer


class ConsecSemLinkDisambiguator(SemLinkDisambiguator):
    def __init__(self, dictionary, debug_mode=False):
        self._token_tagger = TokenTagger()

        self._dictionary = dictionary
        self._debug_mode = debug_mode

        state_dict = torch.load(CONSEC_MODEL_STATE)
        self._sense_extractor = SenseExtractor()
        self._sense_extractor.load_state_dict(state_dict)
        
        self._tokenizer = ConsecTokenizer()

    def _get_definition(self, sense):
        return self._dictionary[sense]["definition"]

    def _get_lemma(self, sense_id):
        return self._dictionary[sense_id]["lemma"]

    def _disambiguate_with_consec(self, sense_id, link_senses):
        # For other links, use Consec to disambiguate by appending the linked lemma to the front.
        if link_senses is None or len(link_senses) == 0:
            return None
        
        if len(link_senses) == 1:
            return link_senses[0]

        lemma = self._get_lemma(sense_id)
        definition = self._get_definition(sense_id)
        definition_tokens = self._token_tagger.tokenize_tag(definition)
        tokens = [lemma] + definition_tokens

        definitions = [ self._get_definition(sense_id) for sense_id in link_senses]

        tokenizer_result = self._tokenizer.tokenize(tokens, 0, definitions, [])
        probs = self._sense_extractor.extract(*tokenizer_result)

        if self._debug_mode:
            sense_idxs = torch.tensor(probs).argsort(descending=True)
            for sense_idx in sense_idxs:
                print(f"{link_senses[sense_idx]}:  {probs[sense_idx]} --- {definitions[sense_idx]}")

        sense_idx = torch.argmax(torch.tensor(probs))
        return link_senses[sense_idx]

    def disambiguate(self, sense_id, link_senses, link_type):    
        if link_type == "SYN":
            return self._disambiguate_synonym(sense_id, link_senses)
        return self._disambiguate_with_consec(sense_id, link_senses)
        