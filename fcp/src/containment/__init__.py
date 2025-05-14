"""Formal containment protocol implementation."""

import typer
from containment.structures import HoareTriple, Specification
from containment.oracles import imp_oracle
from containment.loops import proof_loop
from containment.mcp_server import mcp

__all__ = ["mcp"]


def contain() -> None:
    cli = typer.Typer()

    @cli.command()
    def protocol(
        precondition: str, postcondition: str, max_iterations: int = 25
    ) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        spec = Specification(precondition, postcondition)
        program = imp_oracle(spec)
        if program is None:
            raise ValueError("No program found. Xml parse error probably.")
        triple = HoareTriple(spec, program)
        print(f"Hoare triple: {triple}")
        loop = proof_loop(max_iterations)
        response = loop.run(triple)
        print(f"Proof loop exit code: {response.exit_code}")

    @cli.command()
    def imp_complete(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple with an imp program
        """
        spec = Specification(precondition, postcondition)
        program = imp_oracle(spec)
        print(f"\\{{ {precondition} \\}} {program} \\{{ {postcondition} \\}}")

    cli()


def mcp_server_run() -> None:
    mcp.run()
