class SemLinkSenseProposer():
    def __init__(self, dictionary, sense_inventory):
        self._sense_inventory = sense_inventory
        self._dictionary = dictionary

    def _get_pos(self, sense_id):
        return self._dictionary[sense_id]["pos"]

    def propose_senses(self, sense_id, link_lemma, link_type):
        if link_type == "SYN":
            pos = self._get_pos(sense_id)
            return self._sense_inventory.get_senses_from_lemma(link_lemma, pos)
        return self._sense_inventory.get_senses_from_lemma(link_lemma, "noun")