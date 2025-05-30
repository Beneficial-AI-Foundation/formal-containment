from enum import Enum
from containment.fsio.data import MODEL_DICT


class ModelName(Enum):
    pass


for name, model in MODEL_DICT.items():
    setattr(ModelName, name, model.litellm_id)
