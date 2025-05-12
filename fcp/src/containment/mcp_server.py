import subprocess
import json
from mcp.server.fastmcp import FastMCP
from containment.structures import (
    VerificationResult,
    Specification,
    HoareTriple,
    VerificationResponse,
)

mcp = FastMCP("Formal Containment Process")


@mcp.tool()
def lake_exe_check() -> tuple[int, str, str]:
    """
    Check if `./../imp/` compiles.
    """
    result = subprocess.run(
        ["lake", "exe", "check"], capture_output=True, text=True, cwd="./../imp"
    )
    return result.returncode, result.stdout, result.stderr


@mcp.tool()
def verify_hoare_triple(
    precondition: str, command: str, postcondition: str, context: dict | None = None
) -> str:
    """
    Verify if a given Imp program satisfies its Hoare triple specification.

    Args:
        precondition: Lean expression for the precondition
        command: Imp program to verify
        postcondition: Lean expression for the postcondition
        context: Optional context information for the verification

    Returns:
        A JSON string containing the verification result
    """
    try:
        triple = HoareTriple(
            specification=Specification(
                precondition=precondition, postcondition=postcondition
            ),
            command=command,
        )

        # TODO: Implement actual Hoare triple verification using Lean
        # This should:
        # 1. Send the triple to a proof oracle in one thread
        # 2. Send the negation in another thread
        # 3. Return Pass if positive proof succeeds, Fail if negative proof succeeds

        # Placeholder implementation
        response = VerificationResponse(result=VerificationResult.PASS, triple=triple)

        return json.dumps(
            {
                "result": response.result.value,
                "triple": {
                    "specification": response.triple.specification,
                    "command": response.triple.command,
                },
                "error_message": response.error_message,
            }
        )
    except Exception as e:
        return json.dumps(
            {"result": VerificationResult.FAIL.value, "error_message": str(e)}
        )


@mcp.resource("fcp://specs/{spec_id}")
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
