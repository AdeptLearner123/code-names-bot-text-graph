class TextSenseProposer:
    def __init__(self, sense_inventory):
        self._sense_inventory = sense_inventory
    
    def _assign_multi_word_possibilities(
        self, token_tags, token_senses, length
    ):
        for i in range(len(token_tags) - length + 1):
            span = token_tags[i : i + length]
            span_tokens = [ token for token, _ in span ]

            for _, senses in token_senses[i : i + length]:
                senses += self._sense_inventory.get_senses_from_tokens(span_tokens)

    def _assign_single_word_possibilities(self, token_tags, token_senses):
        for i, (token, tag) in enumerate(token_tags):
            if tag is None:
                continue
            _, senses = token_senses[i]
            senses += self._sense_inventory.get_senses_from_lemma(token, tag)

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
