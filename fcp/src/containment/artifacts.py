from pathlib import Path
import shutil
from datetime import datetime
from containment.structures import HoareTriple

UP = ".."
ARTIFACTS = Path.cwd() / UP / "artifacts"


def write_artifact(tmpdir: Path, triple: HoareTriple) -> Path:
    """
    Write Artifacts.Basic from tmpdir to artifacts/{hash(triple)}.lean.
    """
    target_dir = ARTIFACTS / datetime.now().strftime("%Y%m%d-%H%M")
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        tmpdir / "Artifacts" / "Basic.lean",
        target_dir / f"{hash(triple)}.lean",
    )
    return target_dir
