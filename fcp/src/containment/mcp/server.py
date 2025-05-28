from pathlib import Path
from mcp.server.fastmcp import FastMCP
from containment.structures import (
    Specification,
    HoareTriple,
    LakeResponse,
)
from containment.fsio.prompts import proof_user_prompt, imp_user_prompt
from containment.fsio.lake import Checker
from containment.fsio.tools import temp_lakeproj_init

HEX_ENCODING = "utf-8"
mcp = FastMCP("Formal Containment Process")


@mcp.prompt(
    name="hoare_proof_user_prompt",
    description="Asks the oracle to prove a hoare triple. When stderr is not None, it is the output of the lake tool on a previous attempt.",
)
def get_proof_user_prompt(
    precondition: str, command: str, postcondition: str, metavariables: str, stderr: str
) -> str:
    """
    Get the proof user prompt.

    Args:
        precondition: The precondition of the Hoare Triple
        command: The imp program of the Hoare Triple
        postcondition: The postcondition of the Hoare Triple
        stderr: The standard error output from the lake tool

    Returns:
        A string containing the proof user prompt
    """
    triple = HoareTriple(
        specification=Specification(
            precondition=precondition,
            postcondition=postcondition,
            metavariables=metavariables,
        ),
        command=command,
    )
    if not stderr:
        return proof_user_prompt(triple)
    return proof_user_prompt(triple, stderr)


@mcp.prompt(
    "imp_user_prompt", description="Ask the oracle to fill in the hoare triple."
)
def get_imp_user_prompt(
    precondition: str, postcondition: str, metavariables: str, failed_attempts: str
) -> str:
    """
    Get the user prompt for the imp oracle.

    Args:
        precondition: The precondition of the specification
        postcondition: The postcondition of the specification
        metavariables: " "-separated list of integer Lean variables to be quantified over.
        failed_attempts: Previously attempted imp programs formatted for the prompt
    Returns:
        A string containing the imp user prompt
    """
    return imp_user_prompt(
        Specification(
            precondition=precondition,
            postcondition=postcondition,
            metavariables=metavariables,
        ),
        failed_attempts,
    )


@mcp.tool("typecheck", description="Run the typechecker on the given code.")
def run_lake_exe_check(lean_code: str) -> tuple[Path, LakeResponse]:
    """
    Run the lake exe check command at the given code in a temporary directory.

    Args:
        lean_code: The Lean code to check

    Returns:
        LakeResponse: The result of the lake tool
    """
    cwd = temp_lakeproj_init()
    checker = Checker(cwd=cwd)
    return cwd, checker.run_code(lean_code)
