from enum import Enum


class Polarity(Enum):
    """Whether to affirm or refute the hoare triple. Effects proof template."""

    POS = "Positive"
    NEG = "Negative"


class ProofMethod(Enum):
    """The method used to prove the hoare triple."""

    LOOP = "loop"
    TREE_SEARCH_BASIC = "tree_search_basic"
