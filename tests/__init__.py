from pathlib import Path

ASSET_PATH = "tests/assets"


def get_path(file: str) -> Path:
    """COnstruct full path to the requested file in the tests assets"""
    return Path(ASSET_PATH) / file
