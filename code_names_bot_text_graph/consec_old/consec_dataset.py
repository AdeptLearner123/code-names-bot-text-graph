import torch

from dataclasses import dataclass
from typing import Callable, Iterator, List, NamedTuple, Dict, Any, Optional, Tuple, Iterable
from .disambiguation_corpora import DisambiguationInstance
from .consec_tokenizer import ConsecTokenizer
from .base_dataset import BaseDataset, batchify, batchify_matrices


class ConsecDefinition(NamedTuple):
    text: str
    linker: str  # it can be the instance lemma or text


@dataclass
class ConsecSample:
    sample_id: str
    position: int  # position within disambiguation context
    disambiguation_context: List[DisambiguationInstance]
    candidate_definitions: List[ConsecDefinition]
    context_definitions: List[Tuple[ConsecDefinition, int]]  # definition and position within disambiguation context
    in_context_sample_id2position: Dict[str, int]
    disambiguation_instance: Optional[DisambiguationInstance] = None
    gold_definitions: Optional[List[ConsecDefinition]] = None
    marked_text: Optional[List[str]] = None  # this is set via side-effect
    kwargs: Optional[Dict[Any, Any]] = None

    def reset_context_definitions(self):
        self.marked_text = None
        self.context_definitions = []

    def add_context_definition(self, context_definition: ConsecDefinition, position: int):
        self.context_definitions.append((context_definition, position))

    def get_sample_id_position(self, sample_id: str) -> int:
        return self.in_context_sample_id2position[sample_id]


class ConsecDataset(BaseDataset):
    @classmethod
    def from_samples(cls, samples: Iterator[ConsecSample], **kwargs):
        return cls(lambda: samples, **kwargs)

    def __init__(
        self,
        samples_generator: Callable[[], Iterator[ConsecSample]],
        tokenizer: ConsecTokenizer,
        use_definition_start: bool,
        text_encoding_strategy: str,
        # BaseDataset parameters
        tokens_per_batch: int,
        max_batch_size: Optional[int],
        section_size: int,
        prebatch: bool,
        shuffle: bool,
        max_length: int,
    ):
        super().__init__(
            dataset_iterator_func=None,
            tokens_per_batch=tokens_per_batch,
            max_batch_size=max_batch_size,
            main_field="input_ids",
            fields_batchers=None,
            section_size=section_size,
            prebatch=prebatch,
            shuffle=shuffle,
            max_length=max_length,
        )

        self.samples_generator = samples_generator
        self.tokenizer = tokenizer
        self.use_definition_start = use_definition_start
        self.text_encoding_strategy = text_encoding_strategy
        self._init_fields_batchers()

    def _init_fields_batchers(self) -> None:
        self.fields_batcher = {
            "original_sample": None,  #
            "instance_id": None,  #
            "instance_pos": None,  #
            "instance_lemma": None,  #
            "input_ids": lambda lst: batchify(lst, padding_value=self.tokenizer.pad_token_id),  #
            "attention_mask": lambda lst: batchify(lst, padding_value=0),  #
            "token_type_ids": lambda lst: batchify(lst, padding_value=0),  #
            "original_disambiguation_context": None,  #
            "original_disambiguation_index": None,  #
            "enlarged_disambiguation_context": None,  #
            "enlarged_disambiguation_index": None,  #
            "instance_possible_definitions": None,  #
            "instance_possible_senses": None,  #
            "context_definitions": None,  #
            "context_senses": None,  #
            "depends_from": None,  #
            "definitions_mask": lambda lst: batchify(lst, padding_value=1),  #
            "definitions_offsets": None,  #
            "definitions_positions": None,  #
            "gold_senses": None,
            "gold_definitions": None,  #
            "gold_markers": lambda lst: batchify(lst, padding_value=0),  #
            "relative_positions": lambda lst: batchify_matrices(lst, padding_value=0),
        }

    def create_marked_text(self, sample: ConsecSample) -> List[str]:

        if self.text_encoding_strategy == "simple-with-linker" or self.text_encoding_strategy == "relative-positions":
            disambiguation_context = sample.disambiguation_context
            instance_idx = sample.position

            disambiguation_tokens = [di.text for di in disambiguation_context]
            marked_token = self.tokenizer.mark_token(
                disambiguation_tokens[instance_idx], marker=self.tokenizer.target_marker
            )
            disambiguation_tokens[instance_idx] = marked_token

            return disambiguation_tokens

        else:
            raise ValueError(f"Marking strategy {self.text_encoding_strategy} is undefined")

    def refine_definitions(
        self, sample: ConsecSample, definitions: List[ConsecDefinition], are_context_definitions: bool
    ) -> List[str]:

        if self.text_encoding_strategy == "simple-with-linker":

            # note: this is a direct coupling towards the tokenizer, which gets defined in a different independent yaml
            # file adding a safety assert -> if we are in this branch, tokenizer must have only 1 context_marker
            def_sep_token, def_end_token = self.tokenizer.context_markers[0]
            assert len(self.tokenizer.context_markers) == 1, (
                "Text encoding strategy is simple-with-linker, but multiple context markers, which would be unused, "
                "have been found. Conf error?"
            )

            return [
                f"{definition.capitalize()}. {def_sep_token} {linker} {def_end_token}"
                for definition, linker in definitions
            ]

        elif self.text_encoding_strategy == "relative-positions":
            def_sep_token, def_end_token = self.tokenizer.context_markers[0]
            assert len(self.tokenizer.context_markers) == 1, (
                "Text encoding strategy is simple-with-linker, but multiple context markers, which would be unused, "
                "have been found. Conf error?"
            )
            return [f"{def_sep_token} {definition.text.capitalize().strip('.')}." for definition in definitions]

        else:
            raise ValueError(f"Marking strategy {self.text_encoding_strategy} is undefined")

    def get_definition_positions(
        self, instance_possible_definitions: List[str], definitions_offsets: Dict[str, Tuple[int, int]]
    ) -> List[int]:
        definition_positions = []
        for definition in instance_possible_definitions:
            start_index, end_index = definitions_offsets[definition]
            running_index = start_index if self.use_definition_start else end_index
            definition_positions.append(running_index)
        return definition_positions

    @staticmethod
    def produce_definitions_mask(input_ids: torch.Tensor, definition_positions) -> torch.Tensor:
        definitions_mask = torch.ones_like(input_ids, dtype=torch.float)
        for definition_position in definition_positions:
            definitions_mask[definition_position] = 0.0
        return definitions_mask

    def produce_definition_markers(
        self, input_ids: torch.Tensor, gold_definitions: List[str], definitions_offsets: Dict[str, Tuple[int, int]]
    ) -> torch.Tensor:
        gold_markers = torch.zeros_like(input_ids)
        for definition in gold_definitions:
            start_index, end_index = definitions_offsets[definition]
            running_index = start_index if self.use_definition_start else end_index
            gold_markers[running_index] = 1.0
        return gold_markers

    def dataset_iterator_func(self) -> Iterable[Dict[str, Any]]:

        for sample in self.samples_generator():

            dataset_element = {"original_sample": sample, **sample.kwargs}

            # create marked text
            assert (
                sample.marked_text is None
            ), "Marked text is expected to be set via side-effect, but was found already set"
            sample.marked_text = self.create_marked_text(sample)

            # refine and text-encode definitions
            candidate_definitions = self.refine_definitions(
                sample, sample.candidate_definitions, are_context_definitions=False
            )
            context_definitions = self.refine_definitions(
                sample, [d for d, _ in sample.context_definitions], are_context_definitions=True
            )

            gold_definitions = (
                self.refine_definitions(sample, sample.gold_definitions, are_context_definitions=False)
                if sample.gold_definitions
                else None
            )

            # tokenize
            tokenization_out = self.tokenizer.tokenize(
                sample.marked_text,
                sample.get_sample_id_position(sample.sample_id),
                candidate_definitions,
                [(cd, pos) for cd, (_, pos) in zip(context_definitions, sample.context_definitions)],
            )
            input_ids, attention_mask, token_type_ids, definitions_offsets, relative_positions = tokenization_out
            dataset_element["input_ids"] = input_ids
            dataset_element["attention_mask"] = attention_mask
            dataset_element["definitions_offsets"] = definitions_offsets
            if token_type_ids is not None:
                dataset_element["token_type_ids"] = token_type_ids
            if relative_positions is not None:
                dataset_element["relative_positions"] = relative_positions

            # compute definitions position
            definition_positions = self.get_definition_positions(candidate_definitions, definitions_offsets)
            dataset_element["definitions_positions"] = definition_positions

            # compute definition mask
            definition_mask = self.produce_definitions_mask(input_ids, definition_positions)
            dataset_element["definitions_mask"] = definition_mask

            # create gold markers if present
            if gold_definitions is not None:
                dataset_element["gold_definitions"] = gold_definitions
                dataset_element["gold_markers"] = self.produce_definition_markers(
                    input_ids, gold_definitions, definitions_offsets
                )

            yield dataset_element