import tomllib
from pathlib import Path
import asyncio
from containment.structures import Specification, VerificationResult
from containment.protocol import run as boundary_run

EXPERIMENTS = Path.cwd() / ".." / "experiments"


def load_specifications() -> list[Specification]:
    """
    Load specifications from the experiments directory.
    """
    specs = []
    with open(EXPERIMENTS / "data.toml", "rb") as data:
        samples = tomllib.load(data)
    for sample in samples["samples"]:
        specs.append(Specification(**sample))
    return specs


async def run_experiments(
    specifications: list[Specification], proof_loop_budget: int, attempt_budget: int
) -> list[VerificationResult | None]:
    """
    Run the experiments on the given specifications in parallel
    """
    tasks = [
        boundary_run(
            specification,
            proof_loop_budget=proof_loop_budget,
            attempt_budget=attempt_budget,
        )
        for specification in specifications
    ]
    return await asyncio.gather(*tasks)
