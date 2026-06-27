"""Application version helpers."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
import tomllib


def get_app_version() -> str:
    """Return the local pyproject version, falling back to package metadata."""
    from grii_slide_maker.config import Settings

    pyproject_version = _read_pyproject_version()
    if pyproject_version != Settings.DEFAULT_VERSION:
        return pyproject_version

    try:
        return package_version(Settings.PACKAGE_NAME)
    except PackageNotFoundError:
        return Settings.DEFAULT_VERSION


def _read_pyproject_version() -> str:
    from grii_slide_maker.config import Settings

    for parent in Path(__file__).resolve().parents:
        pyproject_file = parent / "pyproject.toml"
        if pyproject_file.exists():
            with pyproject_file.open("rb") as file:
                return tomllib.load(file)["project"]["version"]

    return Settings.DEFAULT_VERSION
