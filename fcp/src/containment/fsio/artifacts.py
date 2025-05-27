from pathlib import Path
import shutil
import tomli_w
from containment.structures import HoareTriple
from containment.fsio.logs import timestamp

UP = ".."
EXPERIMENTS = Path.cwd() / UP / "experiments"
ARTIFACTS = EXPERIMENTS / "artifacts"

target_dir = ARTIFACTS / timestamp
target_dir.mkdir(parents=True, exist_ok=True)


def write_artifact(tmpdir: Path, triple: HoareTriple) -> Path:
    """
    Write Artifacts.Basic from tmpdir to artifacts/{timestamp}/{hash(triple)}.lean.
    """
    shutil.copyfile(
        tmpdir / "Artifacts" / "Basic.lean",
        target_dir / f"{hash(triple)}.lean",
    )
    return target_dir


def dump_toml(content: dict) -> None:
    """
    Dump the content to a toml file in the artifacts directory at current timestamp
    """
    with open(target_dir / "experiment_results.toml", "wb") as results_file:
        tomli_w.dump(content, results_file)
    return None
