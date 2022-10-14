from typing import NamedTuple, Optional, List

class DisambiguationInstance(NamedTuple):
    document_id: str
    sentence_id: str
    instance_id: str
    text: str
    pos: str
    lemma: str
    labels: Optional[List[str]]