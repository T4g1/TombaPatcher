from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from collections.abc import Iterator

from common import logger


@dataclass
class PatchCommand:
    file_pattern: str
    stage: str | None
    address: int | None
    data: bytes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatchCommand):
            return NotImplemented

        return self.file_pattern == other.file_pattern and (
            (self.address is None and other.address is None)
            or self.address == other.address
        )

    def apply(self, base: Path) -> set[Path]:
        """Apply the patch command
        Returns the list of file modified"""
        updated = set()

        pattern = f"{self.stage}/{self.file_pattern}"
        for file in base.glob(pattern):
            logger.info(f"Patching {file}...")
            if self.address is None:
                with open(file, "wb") as f:
                    f.write(self.data)
            else:
                with open(file, "r+b") as f:
                    f.seek(self.address)
                    f.write(self.data)

            updated.add(file)

        return updated


class Target(BaseModel):
    # Targets all files matching this pattern
    pattern: str

    # Which extraction stage is targetted (GAM, LD, TIM, RLE, ...)
    stage: Optional[str] = "*"

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
            yield PatchCommand(
                target.pattern, stage=target.stage, address=target.address, data=data
            )
