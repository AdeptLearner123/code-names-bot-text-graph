

from typing import Optional

import torch
import pytorch_lightning as pl

from .sense_extractors import DebertaPositionalExtractor

class ConsecPLModule(pl.LightningModule):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.sense_extractor = DebertaPositionalExtractor("microsoft/deberta-large", 0.0, True)
        new_embedding_size = self.sense_extractor.model.config.vocab_size + 203
        self.sense_extractor.resize_token_embeddings(new_embedding_size)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        relative_positions: Optional[torch.Tensor] = None,
        definitions_mask: Optional[torch.Tensor] = None,
        gold_markers: Optional[torch.Tensor] = None,
        *args,
        **kwargs,
    ) -> dict:

        sense_extractor_output = self.sense_extractor.extract(
            input_ids, attention_mask, token_type_ids, relative_positions, definitions_mask, gold_markers
        )

        output_dict = {
            "pred_logits": sense_extractor_output.prediction_logits,
            "pred_probs": sense_extractor_output.prediction_probs,
            "pred_markers": sense_extractor_output.prediction_markers,
            "loss": sense_extractor_output.loss,
        }

        return output_dict