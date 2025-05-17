from binascii import unhexlify
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from containment.structures import (
    Specification,
    HoareTriple,
    LakeResponse,
)
from containment.prompts import proof_user_prompt, imp_user_prompt
from containment.lake import Checker
from containment.tools import temp_lakeproj_init

HEX_ENCODING = "utf-8"
mcp = FastMCP("Formal Containment Process")


@mcp.prompt(
    name="hoare_proof_user_prompt",
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
    name="imp_user_prompt", description="Ask the oracle to fill in the hoare triple."
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


@mcp.tool("unhex", description="Unhex a string")
def unhex_string(hex_string: str) -> str:
    """
    Unhex a string.

    Args:
        hex_string: The hex string to unhex

    Returns:
        str: The unhexed string
    """
    return unhexlify(hex_string).decode(HEX_ENCODING)


@mcp.resource(
    "fcp://specs/{precondition_hex}/{postcondition_hex}",
    name="specification",
    mime_type="application/json",
    description="The specification is a precondition postcondition pair which gets sent to the imp expert to tell it what program to find. Each part is passed in as a hex string and decoded.",
)
def get_specification(precondition_hex: str, postcondition_hex: str) -> Specification:
    """
    Get a specification based on precondition and postcondition.

    Args:
        precondition_hex: The precondition of the specification, in hex format
        postcondition_hex: The postcondition of the specification, in hex format

    Returns:
        Specification: A Specification object containing the precondition and postcondition
    """
    precondition = unhexlify(precondition_hex).decode(HEX_ENCODING)
    postcondition = unhexlify(postcondition_hex).decode(HEX_ENCODING)
    return Specification(precondition=precondition, postcondition=postcondition)


@mcp.resource(
    "fcp://hoare_triples/{precondition_hex}/{command_hex}/{postcondition_hex}",
    name="hoare_triple",
    mime_type="application/json",
    description="The hoare triple gets sent to the proving oracle. Each part is passed in as a hex string and decoded.",
)
def get_hoare_triple(
    precondition_hex: str, command_hex: str, postcondition_hex: str
) -> HoareTriple:
    """
    Get a Hoare Triple based on precondition, command, and postcondition.

    Args:
        precondition_hex: The precondition of the Hoare Triple, in hex format
        command_hex: The imp program of the Hoare Triple, in hex format
        postcondition_hex: The postcondition of the Hoare Triple, in hex format

    Returns:
        HoareTriple: A HoareTriple object containing the specification and command
    """
    precondition = unhexlify(precondition_hex).decode(HEX_ENCODING)
    command = unhexlify(command_hex).decode(HEX_ENCODING)
    postcondition = unhexlify(postcondition_hex).decode(HEX_ENCODING)
    specification = get_specification(precondition, postcondition)
    return HoareTriple(specification=specification, command=command)
