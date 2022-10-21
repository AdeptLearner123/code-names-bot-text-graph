import torch
from torch.utils.data import DataLoader
import numpy as np
from torch.cuda.amp import autocast

from code_names_bot_text_graph.consec_old.pl_modules import ConsecPLModule
from code_names_bot_text_graph.consec_old.consec_tokenizer import DeBERTaTokenizer
from code_names_bot_text_graph.consec_old.consec_dataset import ConsecSample, ConsecDefinition, ConsecDataset
from code_names_bot_text_graph.consec_old.disambiguation_corpora import DisambiguationInstance
from .text_disambiguator import TextDisambiguator

from config import CONSEC_MODEL_STATE

class ConsecTextDisambiguator(TextDisambiguator):
    def __init__(self, dictionary):
        super().__init__(dictionary)

        state_dict = torch.load(CONSEC_MODEL_STATE)

        self._module = ConsecPLModule()
        self._module.sense_extractor.load_state_dict(state_dict)
        self._module.eval()
        self._module.sense_extractor.evaluation_mode = True

        print("Saving")
        torch.save(self._module.sense_extractor.state_dict(), "model_states/consec_semcor_normal_best_sense_extractor.pt")

        self._tokenizer = DeBERTaTokenizer(
            transformer_model="microsoft/deberta-large",
            target_marker=("<d>", "</d>"),
            context_definitions_token="CONTEXT_DEFS",
            context_markers={
                "number":1,
                "pattern":[
                "DEF_SEP",
                "DEF_END"
                ]
            },
            add_prefix_space=True,
            optimize_relative_positions=True,
            enforce_symmetry=False
        )

    def _predict(self, sample):
        device = next(self._module.parameters()).device

        dataset = ConsecDataset.from_samples(
            [ sample ],
            tokenizer=self._tokenizer,
            use_definition_start=True,
            text_encoding_strategy="simple-with-linker",
            tokens_per_batch=1024,
            max_batch_size=128,
            section_size=2_000,
            prebatch=True,
            shuffle=False,
            max_length=self._tokenizer.model_max_length,
        )
        dataloader = DataLoader(dataset, batch_size=None, num_workers=0)

        iterator = dataloader

        for batch in iterator:

            batch_samples = batch["original_sample"]
            batch_definitions_positions = batch["definitions_positions"]

            with autocast(enabled=True):
                with torch.no_grad():
                    batch_out = self._module(**{k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()})
                    batch_predictions = batch_out["pred_probs"]

            for sample, dp, probs in zip(batch_samples, batch_definitions_positions, batch_predictions):
                definition_probs = []
                for start in dp:
                    definition_probs.append(probs[start].item())
                yield sample, definition_probs

    def disambiguate(self, token_senses):
        tokens = [ token for token, _ in token_senses ]
        token_polysemy = [ len(senses) for _, senses in token_senses ]
        indices = np.argsort(token_polysemy)

        disambiguated_senses = [None] * len(token_senses)

        for idx in indices:
            _, senses = token_senses[idx]
            if len(senses) == 0:
                continue
            if len(senses) == 1:
                disambiguated_senses[idx] = senses[0]
                continue
            

            token, senses = token_senses[idx]
            candidate_definitions = [ ConsecDefinition(self._get_definition(sense), "dog") for sense in senses ]
            
            context_definitions = []
            for i, (token, disambiguated_sense) in enumerate(zip(tokens, disambiguated_senses)):
                if disambiguated_sense is None:
                    continue
                context_definitions.append((ConsecDefinition(self._get_definition(disambiguated_sense), token), i))
            
            sample = ConsecSample(
                sample_id="interactive-d0",
                position=idx,
                disambiguation_context=[
                    DisambiguationInstance("d0", "s0", "i0", t, None, None, None) for t in tokens
                ],
                candidate_definitions=candidate_definitions,
                gold_definitions=None,
                context_definitions=context_definitions,
                in_context_sample_id2position={'interactive-d0': idx},
                disambiguation_instance=None,
                kwargs={},
            )

            _, probs = next(self._predict(sample))
            sense_idxs = torch.tensor(probs).argsort(descending=True)

            for sense_idx in sense_idxs:
                print(senses[sense_idx], probs[sense_idx])

            disambiguated_senses[idx] = senses[sense_idxs[0]]

        return disambiguated_senses