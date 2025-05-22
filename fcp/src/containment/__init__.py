"""Formal containment protocol CLI."""

import subprocess
from containment.structures.cli_basic import AsyncTyper
from containment.structures import (
    Specification,
    VerificationSuccess,
    VerificationFailure,
)
from containment.mcp.server import mcp
from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof import ProofExpert
from containment.protocol import run as boundary_run
from containment.fsio.experiment import run_experiments, MODEL_DICT
from containment.fsio.logs import logs


def mcp_server_run() -> None:
    mcp.run(transport="stdio")


def inspector() -> None:
    """
    Run the inspector with `npx`.
    """
    subprocess.run(
        ["npx", "@modelcontextprotocol/inspector", "uv", "run", "mcp-server"]
    )


def test() -> None:
    """
    Test runs.
    """
    cli = AsyncTyper()

    @cli.command()
    async def synthesize_and_prove(
        precondition: str,
        postcondition: str,
        model: str = "anthropic/claude-3-7-sonnet-20250219",
        max_iterations: int = 25,
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)
        expert = await ImpExpert.connect_and_run(model, spec)
        if expert.triple is None:
            raise ValueError("No program found. XML parse error probably.")
        print(expert.triple)
        prover_pos = await ProofExpert.connect_and_run(
            model, expert.triple, positive=True, max_iterations=max_iterations
        )
        if prover_pos.verification_result is None:
            raise ValueError("Prove loop returned None")
        if isinstance(prover_pos.verification_result, VerificationSuccess):
            print("Exit code 0 for code:")
        elif isinstance(prover_pos.verification_result, VerificationFailure):
            print("Exit code 1 for proof:")
        else:
            print("Unknown prover oracle result")
        print(prover_pos.code_dt[-1])
        return None

    @cli.command()
    async def imp_complete(
        precondition: str,
        postcondition: str,
        model: str = "anthropic/claude-3-7-sonnet-20250219",
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple with an imp program
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)

        expert = await ImpExpert.connect_and_run(model, spec)
        print(expert.triple)
        return None

    cli()


def contain() -> None:
    """
    Run the containment protocol.
    """
    cli = AsyncTyper()

    snt = MODEL_DICT["snt4"]

    @cli.command()
    async def protocol(
        precondition: str,
        postcondition: str,
        metavariables: str = "",  # space-separated lean identifiers
        model: str = snt.human_name,
        proof_loop_budget: int = 10,
        attempt_budget: int = 5,
    ) -> None:
        """
        Run the containment protocol at the given precondition-postcondition pair.
        """
        model_id = MODEL_DICT[model].litellm_id
        specification = Specification(
            precondition=precondition,
            postcondition=postcondition,
            metavariables=metavariables,
        )
        msg = f"Running containment protocol at {model_id} for {specification}"
        logs.info(msg)
        print(msg)
        result = await boundary_run(
            model_id,
            specification,
            proof_loop_budget=proof_loop_budget,
            attempt_budget=attempt_budget,
        )

        if result:
            msg = f"({model_id}, {specification}): The following imp code is safe to execute in the world: <imp>{result.triple.command}</imp>"
            logs.info(msg)
            print(msg)
            msg = f"({model_id}, {specification}): The lean code of the proof for you to audit is located in {result.audit_trail}"
            logs.info(msg)
            print(msg)
        else:
            msg = f"({model_id}, {specification}): Failed to find code that is provably safe to run in the world."
            logs.info(msg)
            print(msg)
        return None

    @cli.command()
    async def experiments(
        proof_loop_budget: int = 50, attempt_budget: int = 10
    ) -> None:
        """
        Run the containment protocol experiments from `data.toml`

        TODO: finish configuring logs, metadata
        """
        results = await run_experiments(proof_loop_budget, attempt_budget)
        print(results)
        return None

    cli()
