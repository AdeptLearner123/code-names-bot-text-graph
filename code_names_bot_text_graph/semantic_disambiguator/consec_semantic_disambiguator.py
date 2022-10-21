from code-names-bot-text-graph.code_names_bot_text_graph.consec.sense_extractor import SenseExtractor
import torch

from config import CONSEC_MODEL_STATE
from .semantic_disambiguator import SemanticDisambiguator
from code_names_bot_text_graph.token_tagger.token_tagger import TokenTagger
from code_names_bot_text_graph.consec.sense_extractor import SenseExtractor
from code_names_bot_text_graph.consec.tokenizer import ConsecTokenizer


class ConsecSemanticDisambiguator(SemanticDisambiguator):
    def __init__(self, dictionary, debug_mode):
        super().__init__(dictionary)
        self._token_tagger = TokenTagger()

        self._debug_mode = debug_mode
        state_dict = torch.load(CONSEC_MODEL_STATE)
        self._sense_extractor = SenseExtractor()
        self._sense_extractor.load_state_dict(state_dict)
        
        self._tokenizer = ConsecTokenizer()

    def _get_lemma(self, sense_id):
        return self._dictionary[sense_id]["lemma"]

    def disambiguate(self, sense_id, synonym_senses):
        print("Disambiguating semantic link", synonym_senses, self._get_lemma(sense_id))
        if synonym_senses is None or len(synonym_senses) == 0:
            return None        
        
        if len(synonym_senses) == 1:
            return synonym_senses[0]
    
        definition = self._get_definition(sense_id)
        lemma = self._get_lemma(sense_id)
        definition_tokens = self._token_tagger.tokenize_tag(definition)
        tokens = [lemma] + definition_tokens

        synonym_definitions = [ self._get_definition(sense_id) for sense_id in synonym_senses]

        tokenizer_result = self._tokenizer.tokenize(tokens, 0, synonym_definitions, [])
        probs = self._sense_extractor.extract(*tokenizer_result)

        if self._debug_mode:
            sense_idxs = torch.tensor(probs).argsort(descending=True)
            for sense_idx in sense_idxs:
                print(f"{synonym_senses[sense_idx]}:  {probs[sense_idx]} --- {synonym_definitions[sense_idx]}")

        sense_idx = torch.argmax(torch.tensor(probs))
        return synonym_senses[sense_idx]