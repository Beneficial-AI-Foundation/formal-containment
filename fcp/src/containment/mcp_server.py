import json
from mcp.server.fastmcp import FastMCP
from containment.structures import (
    VerificationResult,
    Specification,
    HoareTriple,
    LakeResponse,
)
from containment.prompts import proof_user_prompt, imp_user_prompt
from containment.lake import Checker
from containment.tools import temp_lakeproj_init
from containment.loops import proof_loop

mcp = FastMCP("Formal Containment Process")


@mcp.prompt(
    name="Hoare triple proof user prompt",
    description="Asks the oracle to prove a hoare triple. When stderr is not None, it is the output of the lake tool on a previous attempt.",
)
def get_proof_user_prompt(triple: HoareTriple, stderr: str | None) -> str:
    """
    Get the proof user prompt.

    Args:
        triple: A Hoare triple containing the specification and command
        stderr: The standard error output from the lake tool

    Returns:
        A string containing the proof user prompt
    """
    return proof_user_prompt(triple, stderr)


@mcp.prompt(
    name="Imp user prompt", description="Ask the oracle to fill in the hoare triple."
)
def get_imp_user_prompt(spec: Specification) -> str:
    """
    Get the user prompt for the imp oracle.

    Args:
        spec: A specification containing the precondition and postcondition

    Returns:
        A string containing the imp user prompt
    """
    return imp_user_prompt(spec)


@mcp.tool("Run the typechecker on the given code.")
def run_lake_exe_check(lean_code: str) -> LakeResponse:
    """
    Run the lake exe check command.

    Args:
        lean_code: The Lean code to check

    Returns:
        LakeResponse: The result of the lake tool
    """
    cwd = temp_lakeproj_init()
    checker = Checker(cwd)
    return checker.run_code(lean_code)


@mcp.tool("Attempt to prove a hoare triple.")
def run_proof_loop_pos(triple: HoareTriple) -> VerificationResult | None:
    """
    Verify if a given Imp program satisfies its Hoare triple specification.

    Args:
        triple: A hoare triple containing the specification and command

    Returns:
        A VerificationResult
    """
    loop = proof_loop(max_iterations=25)
    return loop.run(triple, positive=True)


@mcp.tool("Attempt to prove the negation of a hoare triple.")
def run_proof_loop_neg(triple: HoareTriple) -> VerificationResult | None:
    """
    Verify if a given Imp program satisfies its Hoare triple specification.

    Args:
        triple: A hoare triple containing the specification and command

    Returns:
        A VerificationResult
    """
    loop = proof_loop(max_iterations=25)
    return loop.run(triple, positive=False)


@mcp.resource("fcp://specs/{spec_id}", name="Hoare triple specification")
def get_hoare_spec(spec_id: str) -> str:
    """
    Get a specific Hoare triple specification by ID.

    Args:
        spec_id: The ID of the specification to retrieve

    Returns:
        A JSON string containing the specification
    """
    # TODO: Implement actual specification retrieval
    # This should fetch stored specifications from a database or file system

    spec = {
        "id": spec_id,
        "precondition": "λ st. st X > 0",
        "postcondition": "λ st. st X > 1",
        "description": "Example specification from whitepaper",
    }

    return json.dumps(spec)


@mcp.resource("fcp://triples/{triple_hash}")
def get_hoare_triple(triple_hash: str) -> str:
    return triple_hash
