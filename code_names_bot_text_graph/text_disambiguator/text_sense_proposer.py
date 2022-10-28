class TextSenseProposer:
    def __init__(self, sense_inventory):
        self._sense_inventory = sense_inventory
    
    def _assign_multi_word_possibilities(
        self, token_tags, token_senses, compound_indices, length
    ):
        for i in range(len(token_tags) - length + 1):
            span = token_tags[i : i + length]
            span_tokens = [ token for token, _ in span ]
            senses_from_tokens = self._sense_inventory.get_senses_from_tokens(span_tokens)

            for _, senses in token_senses[i : i + length]:
                senses += senses_from_tokens

            for sense in senses_from_tokens:
                compound_indices.append((sense, (i, i + length)))

    def _assign_single_word_possibilities(self, token_tags, token_senses):
        for i, (token, tag) in enumerate(token_tags):
            if tag is None:
                continue
            _, senses = token_senses[i]
            senses += self._sense_inventory.get_senses_from_lemma(token, tag)

    def propose_senses(self, token_tags):
        token_senses = [(token, []) for token, _ in token_tags]
        compound_indices = []

        for length in range(2, 5):
            self._assign_multi_word_possibilities(
                token_tags, token_senses, compound_indices, length
            )
        self._assign_single_word_possibilities(
            token_tags, token_senses
        )

        # Tokens with None tag (stop word) should not have any senses.
        # Otherwise compound words that conatin stop words will always have the stop word assigned to that sense.
        # Ex: The sense for "come to" will always have "to" disambiguated to that sense, even if "come to" is not the right sense for "come".
        for i, (token, tag) in enumerate(token_tags):
            if tag is None:
                token_senses[i] = (token, [])

        # Remove duplicates
        # Sort sense ids so that proposed senses are deterministic.
        token_senses = [(token, sorted(list(set(senses)))) for token, senses in token_senses]

        return token_senses, compound_indices
