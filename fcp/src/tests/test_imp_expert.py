import pytest
from containment.structures import Specification, HoareTriple
from containment.mcp.clients.experts.imp import ImpExpert
from containment.fsio.data import MODEL_DICT


@pytest.mark.asyncio
async def test_imp_expert_synthesize(
    sample_specification: Specification,
):
    """Test the synthesis of a Hoare triple using the ImpExpert."""
    expert = await ImpExpert.connect_and_run(
        MODEL_DICT["hku35"].litellm_id, sample_specification
    )

    assert isinstance(expert, ImpExpert)
    assert expert.triple is not None
    assert isinstance(expert.triple, HoareTriple)
    assert expert.triple.specification == sample_specification
    assert expert.triple.command.startswith("imp {")
