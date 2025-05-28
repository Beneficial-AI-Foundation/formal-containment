import tempfile
import shutil
import subprocess
from pathlib import Path
from pantograph import Server
from containment.structures import LakeResponse

CMD = ["lake", "exe", "check"]
UP = ".."
LAKE_DIR = Path.cwd() / UP / "imp"


def lake_exe_check(cwd: Path) -> LakeResponse:
    """
    Run `lake exe check` in the given directory.

    Assumes: a properly formed lake project is in the directory.
    """
    result = subprocess.run(CMD, text=True, capture_output=True, cwd=cwd)

    return LakeResponse.from_subprocess_result(result)


def temp_lakeproj_init(lake_dir: Path = LAKE_DIR) -> Path:
    """
    Copies the lake project to a temporary directory. We're allowing stale tmp files because we want to pass around the tmpdir without worrying about it getting cleaned up.
    """
    tmpdir = Path(tempfile.mkdtemp())
    shutil.copytree(
        lake_dir,
        tmpdir,
        dirs_exist_ok=True,
    )
    return tmpdir


def pantograph_init(cwd: Path) -> Server:
    """
    Initialize the Pantograph server.
    """
    server = Server(
        project_path=str(cwd),
    )
    return server
