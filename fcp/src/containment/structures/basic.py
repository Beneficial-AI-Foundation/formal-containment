import json
from pydantic import BaseModel


class Structure(BaseModel):
    """
    Base class for all structures.
    """

    @property
    def jsons(self) -> str:
        """JSON string."""
        return json.dumps(self.model_dump())

    @property
    def dictionary(self) -> dict:
        """Serializable dictionary."""
        return json.loads(self.model_dump_json())
