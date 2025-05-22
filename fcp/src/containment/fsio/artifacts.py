from pathlib import Path
import shutil
from containment.structures import HoareTriple
from containment.fsio.logs import timestamp

UP = ".."
ARTIFACTS = Path.cwd() / UP / "experiments" / "artifacts"


def write_artifact(tmpdir: Path, triple: HoareTriple) -> Path:
    """
    Write Artifacts.Basic from tmpdir to artifacts/{timestamp}/{hash(triple)}.lean.
    """
    target_dir = ARTIFACTS / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        tmpdir / "Artifacts" / "Basic.lean",
        target_dir / f"{hash(triple)}.lean",
    )
    return target_dir
