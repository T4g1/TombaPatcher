from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal
from pathlib import Path

from patcher.patcher import patch

OUTPUT_FILES = "output/files"


@dataclass
class PatchCommand:
    file_pattern: str
    address: int
    data: bytes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatchCommand):
            return NotImplemented

        return self.file_pattern == other.file_pattern and self.address == other.address


class PatchWorker(QThread):
    status_changed = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, filepath: str, patches: list[PatchCommand]):
        super().__init__()

        self.filepath = Path(filepath)
        self.outputpath = (
            self.filepath.parent / f"{self.filepath.stem}.patched{self.filepath.suffix}"
        )

    def run(self):
        try:
            patch(self.filepath, self.outputpath)
            self.finished.emit(True, "Game successfully patched !")
        except Exception as exception:
            self.finished.emit(False, f"Error during patching process: {exception}")
