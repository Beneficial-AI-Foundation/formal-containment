import tempfile
import shutil
import subprocess
import atexit
from pathlib import Path
from pantograph import Server
from containment.structures import LakeResponse

CMD = ["lake", "exe", "check"]
UP = ".."
LAKE_DIR = Path.cwd() / UP / "imp"

# Keep track of temporary directories to clean up
_temp_dirs = set()


def _cleanup_temp_dirs():
    """Clean up all temporary directories created during script execution."""
    for tmpdir in _temp_dirs:
        try:
            shutil.rmtree(tmpdir)
        except Exception as e:
            print(f"Error cleaning up temporary directory {tmpdir}: {e}")


# Register cleanup function to run at exit
atexit.register(_cleanup_temp_dirs)


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
    _temp_dirs.add(tmpdir)  # Add to set of directories to clean up
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
