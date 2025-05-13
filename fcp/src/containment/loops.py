import tempfile
from typing import Callable
from pathlib import Path
import shutil
from containment.structures import ToolResponse
from containment.prompts import get_oracle_system_prompt
from containment.oracles import Oracle
from containment.tools import lake_exe_check

UP = ".."
CWD = Path(".") / UP / "imp"


class Loop:
    def __init__(
        self,
        system_prompt: str,
        tool: Callable[[Path], ToolResponse],
        working_dir: Path,
    ):
        self.oracle = Oracle(system_prompt)
        self.tool = tool
        self.working_dir = working_dir

    def _loop_init(self) -> ToolResponse:
        return ToolResponse(1, "TODO", "TODO")

    def run_tool(self) -> ToolResponse:
        """
        Run the tool and return the result.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            shutil.copytree(
                self.working_dir,
                tmpdir,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".lake/"),
            )
            result = self.tool(tmpdir)
        return result

    # TODO: implement stateful loop that feeds error message from tool use back into oracle


proof_system_prompt = get_oracle_system_prompt("proof")
proof_loop = Loop(proof_system_prompt, lake_exe_check, CWD)
