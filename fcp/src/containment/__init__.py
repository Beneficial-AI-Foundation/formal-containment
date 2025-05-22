"""Formal containment protocol CLI."""

import subprocess
from typer import Typer
from containment.structures.cli_basic import AsyncTyper
from containment.structures import (
    HoareTriple,
    Specification,
    VerificationSuccess,
    VerificationFailure,
)
from containment.oracles import imp_oracle
from containment.loops import proof_loop
from containment.mcp.server import mcp
from containment.mcp.clients.experts.imp import ImpExpert
from containment.mcp.clients.experts.proof import ProofExpert
from containment.protocol import run as boundary_run
from containment.io.experiment import load_specifications, run_experiments


def mcp_server_run() -> None:
    mcp.run(transport="stdio")


def test_no_mcp() -> None:
    """
    MCP-free test runs.

    Pretty defunct.
    """
    cli = Typer()

    @cli.command()
    def synthesize_and_prove(
        precondition: str, postcondition: str, max_iterations: int = 25
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it, without MCP.
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)
        program = imp_oracle(spec)
        if program is None:
            raise ValueError("No program found. XML parse error probably.")
        triple = HoareTriple(specification=spec, command=program)
        print(f"Hoare triple: {triple}")
        loop = proof_loop(max_iterations)
        result = loop.run(triple, positive=True)
        if isinstance(result, VerificationSuccess):
            msg = f"Exit code 0 at proof={result.proof}"
        elif isinstance(result, VerificationFailure):
            msg = f"Exit code 1 at proof={result.proof} with error: {result.error_message}"
        else:
            msg = "Unknown result. Probably an XML parse error"
        print(msg)
        return None

    @cli.command()
    def imp_complete(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple with an imp program
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)
        program = imp_oracle(spec)
        if program is None:
            raise ValueError("No program found. Xml parse error probably.")
        print(HoareTriple(specification=spec, command=program))
        return None

    cli()


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
        precondition: str, postcondition: str, max_iterations: int = 25
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)
        expert = await ImpExpert.connect_and_run(spec)
        if expert.triple is None:
            raise ValueError("No program found. XML parse error probably.")
        print(expert.triple)
        prover_pos = await ProofExpert.connect_and_run(
            expert.triple, positive=True, max_iterations=max_iterations
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
    async def imp_complete(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple with an imp program
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)

        expert = await ImpExpert.connect_and_run(spec)
        print(expert.triple)
        return None

    cli()


def contain() -> None:
    """
    Run the containment protocol.
    """
    cli = AsyncTyper()

    @cli.command()
    async def protocol(
        precondition: str,
        postcondition: str,
        metavariables: str = "",  # space-separated lean identifiers
        proof_loop_budget: int = 10,
        attempt_budget: int = 5,
    ) -> None:
        """
        Run the containment protocol at the given precondition-postcondition pair.
        """
        specification = Specification(
            precondition=precondition,
            postcondition=postcondition,
            metavariables=metavariables,
        )
        result = await boundary_run(
            specification,
            proof_loop_budget=proof_loop_budget,
            attempt_budget=attempt_budget,
        )

        if result:
            print(
                f"The following imp code is safe to execute in the world: <imp>{result.triple.command}</imp>"
            )
            print(
                f"The lean code of the proof for you to audit is located in {result.audit_trail}"
            )
        else:
            print("Failed to find code that is provably safe to run in the world.")
        return None

    @cli.command()
    async def experiments(
        proof_loop_budget: int = 50, attempt_budget: int = 10
    ) -> None:
        """
        Run the containment protocol experiments from `data.toml`
        """
        specifications = load_specifications()
        results = await run_experiments(
            specifications, proof_loop_budget, attempt_budget
        )
        print(results)
        return None

    cli()
