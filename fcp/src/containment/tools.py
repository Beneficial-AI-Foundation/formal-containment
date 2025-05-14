from pathlib import Path
import subprocess
from containment.structures import ToolResponse

CMD = ["lake", "exe", "check"]
UP = ".."


def lake_exe_check(cwd: Path = Path.cwd() / UP / "imp") -> ToolResponse:
    """
    Run `lake exe check` in the given directory.

    Assumes: a properly formed lake project is in the directory.
    """
    result = subprocess.run(CMD, text=True, capture_output=True, cwd=cwd)

    return ToolResponse.from_subprocess_result(result)
