import torch

from .text_disambiguator import TextDisambiguator
from config import CONSEC_MODEL_STATE
from code_names_bot_text_graph.consec.disambiguation_instance import ConsecDisambiguationInstance
from code_names_bot_text_graph.consec.sense_extractor import SenseExtractor
from code_names_bot_text_graph.consec.tokenizer import ConsecTokenizer

class ConsecTextDisambiguator(TextDisambiguator):
    def __init__(self, dictionary, debug_mode=False):
        super().__init__(dictionary)

        self._debug_mode = debug_mode
        state_dict = torch.load(CONSEC_MODEL_STATE)
        self._sense_extractor = SenseExtractor()
        self._sense_extractor.load_state_dict(state_dict)
        self._sense_extractor.eval()
        self._tokenizer = ConsecTokenizer()

        if torch.cuda.is_available():
            self._sense_extractor.cuda()
    
    def _get_disambiguation_order(self, token_senses):
        disambiguated_senses = [None] * len(token_senses)

        token_polysemy = []
        for i, (_, senses) in enumerate(token_senses):
            if len(senses) == 1:
                disambiguated_senses[i] = senses[0]
            elif len(senses) > 1:
                token_polysemy.append((i, len(senses)))

        token_polysemy = sorted(token_polysemy, key=lambda item:item[1])
        disambiguation_order = [ i for i, _ in token_polysemy]
        return disambiguated_senses, disambiguation_order

    def disambiguate(self, token_senses, compound_indices):
        disambiguation_instance = ConsecDisambiguationInstance(self._dictionary, self._tokenizer, token_senses, compound_indices)

        while not disambiguation_instance.is_finished():
            input, (senses, definitions) = disambiguation_instance.get_next_input()
            if torch.cuda.is_available():
                input = self._send_inputs_to_cuda(input)

            probs = self._sense_extractor.extract(*input)

            if self._debug_mode:
                sense_idxs = torch.tensor(probs).argsort(descending=True)
                for sense_idx in sense_idxs:
                    print(f"{senses[sense_idx]}:  {probs[sense_idx]} --- {definitions[sense_idx]}")

            sense_idx = torch.argmax(torch.tensor(probs))
            disambiguation_instance.set_result(senses[sense_idx])

        return disambiguation_instance.get_disambiguated_senses(), []

    def _send_inputs_to_cuda(self, inputs):
        (input_ids, attention_mask, token_types, relative_pos, def_mask, def_pos) = inputs

        input_ids = input_ids.cuda()
        attention_mask = attention_mask.cuda()
        token_types = token_types.cuda()
        relative_pos = relative_pos.cuda()
        def_mask = def_mask.cuda()

        return (input_ids, attention_mask, token_types, relative_pos, def_mask, def_pos)

    def batch_disambiguate(self, token_senses_compound_indices_list):
        instances = [ ConsecDisambiguationInstance(self._dictionary, self._tokenizer, token_senses, compound_indices) for token_senses, compound_indices in token_senses_compound_indices_list]

        round = 0
        while any([ not instance.is_finished() for instance in instances ]):
            round += 1

            inputs_list = []
            senses_list = []
            active_instances = []

            for instance in instances:
                if not instance.is_finished():
                    inputs, (senses, _) = instance.get_next_input()

                    if torch.cuda.is_available():
                        inputs = self._send_inputs_to_cuda(inputs)

                    active_instances.append(instance)
                    inputs_list.append(inputs)
                    senses_list.append(senses)

            inputs_list = list(zip(*inputs_list))
            probs_list = self._sense_extractor.batch_extract(*inputs_list)

            for probs, senses, instance in zip(probs_list, senses_list, active_instances):
                sense_idx = torch.argmax(torch.tensor(probs))
                instance.set_result(senses[sense_idx])

        return [ instance.get_disambiguated_senses() for instance in instances ]