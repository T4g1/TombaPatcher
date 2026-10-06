from PySide6.QtCore import QThread, Signal
from pathlib import Path

from patcher.patcher import Patcher


class PatchWorker(QThread):
    status_changed = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, filepath: str):
        super().__init__()

        self.filepath = Path(filepath)
        self.outputpath = (
            self.filepath.parent / f"{self.filepath.stem}.patched{self.filepath.suffix}"
        )
        self.patcher = Patcher()

    def run(self):
        try:
            self.patcher.patch(self.filepath, self.outputpath)
            self.finished.emit(True, "Game successfully patched !")
        except Exception as exception:
            self.finished.emit(False, f"Error during patching process: {exception}")
