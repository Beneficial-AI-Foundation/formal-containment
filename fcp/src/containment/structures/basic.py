import json
from pydantic import BaseModel


class Structure(BaseModel):
    """
    Base class for all structures.
    """

    @property
    def jsons(self) -> str:
        return json.dumps(self.model_dump())
