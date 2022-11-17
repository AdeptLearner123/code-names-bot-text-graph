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
            span_senses = set.intersection(*[ set(senses) for _, senses in token_senses[i:i + length] ])
            # If the compound sense was already added in a previous iteration, ignore.
            # Ex: If "The Amazing Spider-Man" has already been added, then ignore "Spider-Man"
            senses_from_tokens = list(set(senses_from_tokens).difference(span_senses))

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

    def _get_proper_chunks(self, token_tags):
        proper_chunks = []
        current_start = None
        for i, (_, tag) in enumerate(token_tags):
            if tag != "proper":
                if current_start is not None:
                    proper_chunks.append((current_start, i))
                    current_start = None
            else:
                if current_start is None:
                    current_start = i
        if current_start is not None:
            proper_chunks.append((current_start, len(token_tags)))
        return proper_chunks

    def _unassign_proper_fragments(self, token_tags, token_senses):
        proper_chunks = self._get_proper_chunks(token_tags)
        for begin, end in proper_chunks:
            senses_list = [ set(senses) for _, senses in token_senses[begin:end] ]
            tokens_list = [ token for token, _ in token_senses[begin:end] ]
            filtered_senses = set.intersection(*senses_list)
            token_senses[begin:end] = zip(tokens_list, [list(filtered_senses)] * (end - begin))

    def propose_senses(self, token_tags):
        token_senses = [(token, []) for token, _ in token_tags]
        compound_indices = []

        for length in range(5, 1, -1):
            # Iterate backwards since short versions of a compound should not be added if the long version of the compound has already been added.
            self._assign_multi_word_possibilities(
                token_tags, token_senses, compound_indices, length
            )
        self._assign_single_word_possibilities(
            token_tags, token_senses
        )

        print(token_tags)
        print(compound_indices)

        #self._unassign_proper_fragments(token_tags, token_senses)
        
        # Tokens that are stop words should not have any senses.
        # Otherwise compound words that conatin stop words will always have the stop word assigned to that sense.
        # Ex: The sense for "come to" will always have "to" disambiguated to that sense, even if "come to" is not the right sense for "come".
        for i, (token, tag) in enumerate(token_tags):
            if tag == "STOP":
                token_senses[i] = (token, [])

        # Remove duplicates
        # Sort sense ids so that proposed senses are deterministic.
        token_senses = [(token, sorted(list(set(senses)))) for token, senses in token_senses]

        return token_senses, compound_indices
