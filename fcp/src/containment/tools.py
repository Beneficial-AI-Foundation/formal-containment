from pathlib import Path
import subprocess
from containment.structures import ToolResponse

CMD = ["lake", "exe", "check"]
UP = ".."


def lake_exe_check(cwd: Path = Path(".") / UP / "imp") -> ToolResponse:
    result = subprocess.run(CMD, text=True, capture_output=True, cwd=cwd)

    return ToolResponse.from_subprocess_result(result)
