class SynonymSenseProposer():

    def __init__(self, sense_inventory):
        self._sense_inventory = sense_inventory

    def get_senses(self, lemma, pos):
        key = f"{lemma}|{pos}"

        if key in self._sense_inventory:
            return self._sense_inventory[key]
        if lemma in self._sense_inventory:
            return self._sense_inventory[lemma]
        return []