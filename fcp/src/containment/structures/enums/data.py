from enum import Enum, EnumMeta
from containment.fsio.data import MODEL_DICT


class ModelNameMeta(EnumMeta):
    """For dynamically building an Enum from MODEL_DICT, for use with typer."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Add dynamic members to namespace before enum creation
        for model_name, _ in MODEL_DICT.items():
            if not model_name.isidentifier():
                raise ValueError(f"Invalid model name: {model_name}")
            namespace[model_name] = model_name
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class ModelName(str, Enum, metaclass=ModelNameMeta):
    pass
