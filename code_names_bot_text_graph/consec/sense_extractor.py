import torch
import torch.nn as nn
from transformers import DebertaPreTrainedModel
from transformers.models.deberta.modeling_deberta import DebertaEmbeddings, DebertaEncoder

class ConsecDebertaModel(DebertaPreTrainedModel):
    def __init__(self, config):
        print("Init ConsecDeberatModel")
        super().__init__(config)

        self.embeddings = DebertaEmbeddings(config)

        # DebertaEncoder source code: https://huggingface.co/transformers/v4.7.0/_modules/transformers/models/deberta/modeling_deberta.html
        self.encoder = DebertaEncoder(config)

    def get_input_embeddings(self):
        return self.embeddings.word_embeddings

    def set_input_embeddings(self, new_embeddings):
        self.embeddings.word_embeddings = new_embeddings

    def forward(self, input_ids, attention_mask, token_types, relative_pos):
        embedding_output = self.embeddings(
            input_ids=input_ids,
            token_type_ids=token_types,
            mask=attention_mask,
        )

        # This returns a BaseModelOutput
        encoder_outputs = self.encoder(
            embedding_output,
            attention_mask,
            output_hidden_states=True,
            relative_pos=relative_pos,
        )

        # NOTE: Original code gets encoder_outputs[1][-1]
        sequence_output = encoder_outputs[0]

        # NOTE: This is different from original
        return sequence_output


class SenseExtractor(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = ConsecDebertaModel.from_pretrained("microsoft/deberta-large")

        self.model.resize_token_embeddings(self.model.config.vocab_size + 203)

        self.classification_head = torch.nn.Sequential(
            torch.nn.Dropout(0.0), torch.nn.Linear(self.model.config.hidden_size, 1, bias=False)
        )

    def _compute_markers(self, input_ids, logits):
        output_markers = torch.zeros_like(input_ids)
        markers_positions = torch.argmax(logits, dim=-1, keepdim=True)
        output_markers = output_markers.scatter(1, markers_positions, 1.0)
        return output_markers

    def _mask_logits(self, logits, logits_mask):
        return logits * (1 - logits_mask) - 1e30 * logits_mask
    
    def forward(self, input_ids, attention_mask, token_types, relative_pos):
        model_out = self.model(input_ids, attention_mask, token_types, relative_pos)
        classification_logits = self.classification_head(model_out).squeeze(-1)
        return classification_logits

    def extract(self, input_ids, attention_mask, token_types, relative_pos, definitions_mask, definition_positions):
        # Add dummy batch dimension
        input_ids = input_ids[None]
        attention_mask = attention_mask[None]
        token_types = token_types[None]
        relative_pos = relative_pos[None]
        definitions_mask = definitions_mask[None]

        classification_logits = self.forward(input_ids, attention_mask, token_types, relative_pos)
        classification_logits = self._mask_logits(classification_logits, definitions_mask)
        prediction_probs = torch.softmax(classification_logits, dim=-1)
        prediction_probs = prediction_probs.squeeze(0)

        definition_probs = []
        for idx in definition_positions:
            definition_probs.append(prediction_probs[idx].item())
        return definition_probs