"""Formal containment protocol implementation."""

import typer
from containment.structures import Specification
from containment.oracles import imp_oracle
from containment.mcp_server import mcp

__all__ = ["mcp"]


def contain() -> None:
    cli = typer.Typer()

    @cli.command()
    def protocol(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        print(f"Precondition: {precondition}")
        print(f"Postcondition: {postcondition}")
        spec = Specification(precondition, postcondition)
        program_completion = imp_oracle(spec)
        print(f"Program completion: {program_completion}")

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
