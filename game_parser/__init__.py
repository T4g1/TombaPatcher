from pathlib import Path


def consume_suffix(path: Path) -> Path:
    return path.with_suffix("")


def add_suffix(path: Path, suffix: str) -> Path:
    return path.with_suffix(f"{path.suffix}{suffix}")


def get_token(path: Path) -> str:
    stem = path.name.split(".")[0]

    if "-" not in stem:
        raise ValueError(f"Trying to get token from {path} but there are none")

    _, token = stem.rsplit("-", 1)

    return token


def consume_token(path: Path) -> Path:
    stem = path.name.split(".")[0]
    extension = "".join(path.suffixes)

    if "-" not in stem:
        raise ValueError(f"Trying to consume token from {path} but there are none")

    stem, _ = stem.rsplit("-", 1)

    return path.with_name(f"{stem}{extension}")


def add_token(path: Path, token: str) -> Path:
    stem = path.name.split(".")[0]
    extension = "".join(path.suffixes)

    return path.with_name(f"{stem}-{token}{extension}")


class Parser:
    """
    Every file type parser must inherit from this class.
    It defines how to process a file forward and how to reverse it.
    """

    @staticmethod
    def forward(input: Path, params: dict[str, int] = {}) -> Path | list[Path]:
        """Processes the file and returns a list of resulting file paths"""
        raise NotImplementedError

    @staticmethod
    def reverse(input: Path | list[Path], params: dict[str, int] = {}) -> Path:
        """Takes either a single file or a list of files, recombines them, and reverses modifications"""
        raise NotImplementedError
