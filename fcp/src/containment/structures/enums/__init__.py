from enum import Enum


class Polarity(str, Enum):
    """Whether to affirm or refute the hoare triple. Effects proof template."""

    POS = "Positive"
    NEG = "Negative"


class ProofMethod(str, Enum):
    """The method used to prove the hoare triple."""

    LOOP = "loop"
    TREE_SEARCH_BASIC = "tree_search_basic"
