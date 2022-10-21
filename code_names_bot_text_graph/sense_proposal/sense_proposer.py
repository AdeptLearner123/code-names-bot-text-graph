from config import SENSE_INVENTORY


class SenseProposer:
    def __init__(self, sense_inventory):
        self._sense_inventory = sense_inventory
    
    def _assign_multi_word_possibilities(
        self, token_tags, token_senses, length
    ):
        for i in range(len(token_tags) - length + 1):
            span = token_tags[i : i + length]
            span_tokens = [ token for token, _ in span ]
            span_key = ' '.join(span_tokens)

            if span_key in self._sense_inventory:
                for _, senses in token_senses[i : i + length]:
                    senses += self._sense_inventory[span_key]

    def _assign_single_word_possibilities(self, token_tags, token_senses):
        for i, (token, tag) in enumerate(token_tags):
            if tag is None:
                continue

            key = f"{token}|{tag}"

            if key in self._sense_inventory:
                _, senses = token_senses[i]
                senses += self._sense_inventory[key]

    def propose_senses(self, token_tags):
        token_senses = [(token, []) for token, _ in token_tags]

        for length in range(2, 5):
            self._assign_multi_word_possibilities(
                token_tags, token_senses, length
            )
        self._assign_single_word_possibilities(
            token_tags, token_senses
        )

        # Remove duplicates
        # Sort sense ids so that proposed senses are deterministic.
        token_senses = [(token, sorted(list(set(senses)))) for token, senses in token_senses]

        return token_senses
