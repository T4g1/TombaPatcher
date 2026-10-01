from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from collections.abc import Iterator


@dataclass
class PatchCommand:
    file_pattern: str
    address: int | None
    data: bytes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatchCommand):
            return NotImplemented

        return self.file_pattern == other.file_pattern and (
            (self.address is None and other.address is None)
            or self.address == other.address
        )


class Target(BaseModel):
    # Targets all files matching this pattern
    pattern: str

    # Specific address in the matched files
    address: Optional[int] = None


class Patch(BaseModel):
    # Path to the file containing the new data
    file: str

    # List of targets to apply that file
    targets: list[Target]

    def commands(self, base: Path) -> Iterator[PatchCommand]:
        with open(base / self.file, "rb") as f:
            data = f.read()

        for target in self.targets:
            yield PatchCommand(target.pattern, address=target.address, data=data)
