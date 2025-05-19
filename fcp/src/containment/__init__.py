"""Formal containment protocol CLI."""

import subprocess
from typer import Typer
from containment.structures import (
    HoareTriple,
    Specification,
    VerificationSuccess,
    VerificationFailure,
)
from containment.oracles import imp_oracle
from containment.loops import proof_loop
from containment.mcp.server import mcp
from containment.mcp.clients.boundary import Boundary
from containment.mcp.clients.completion import ImpExpert, ProofExpert
from containment.structures.cli_basic import AsyncTyper


def test() -> None:
    """MCP-free test run."""
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


def mcp_server_run() -> None:
    mcp.run(transport="stdio")


def inspector() -> None:
    """
    Run the inspector with `npx`.
    """
    subprocess.run(
        ["npx", "@modelcontextprotocol/inspector", "uv", "run", "mcp-server"]
    )


def main() -> None:
    """
    Containment protocol CLI.
    """
    cli = AsyncTyper()

    @cli.command("protocol")
    def protocol(
        precondition: str, postcondition: str, max_iterations: int = 25
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)
        boundary = Boundary(spec)

        return None

    @cli.command("imp-complete")
    async def imp_complete(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple with an imp program
        """
        spec = Specification(precondition=precondition, postcondition=postcondition)

        expert = await ImpExpert.connect_and_run(spec)
        print(expert.triple)
        return None

    cli()
