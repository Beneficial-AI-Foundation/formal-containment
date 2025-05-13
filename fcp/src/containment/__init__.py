"""Formal containment protocol implementation."""

import typer
from containment.structures import HoareTriple, Specification
from containment.oracles import imp_oracle, proof_oracle
from containment.mcp_server import mcp

__all__ = ["mcp"]


def contain() -> None:
    cli = typer.Typer()

    @cli.command()
    def protocol(precondition: str, postcondition: str) -> None:
        """
        Take a precondition and postcondition and ask the LLM to fill in the hoare triple and prove it.
        """
        spec = Specification(precondition, postcondition)
        program = imp_oracle(spec)
        if program is None:
            raise ValueError("No program found")
        triple = HoareTriple(spec, program)
        print(f"Hoare triple: {triple}")
        proof = proof_oracle(triple)
        if proof is None:
            raise ValueError("No proof found")
        print(f"Proof: {proof}")

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
