from enum import Enum
from PySide6.QtCore import QThread, Signal
from pathlib import Path

from patcher.patcher import Patcher


class PatchWorkerMode(Enum):
    ALL = "all"
    EXTRACT = "exctract"
    PATCH = "patch"
    COMPILE = "compile"


class PatchWorker(QThread):
    status_changed = Signal(str)
    finished = Signal(bool, str)

    running: bool = False
    mode: PatchWorkerMode = PatchWorkerMode.ALL

    def __init__(self):
        super().__init__()

        self.patcher = Patcher(with_context=True)

    def set_filepath(self, filepath: str):
        self.filepath = Path(filepath)
        self.outputpath = (
            self.filepath.parent / f"{self.filepath.stem}.patched{self.filepath.suffix}"
        )

    def _start(self, status: str):
        self.running = True
        self.status_changed.emit(status)

    def _finish(self, success: bool, message: str):
        self.running = False
        self.finished.emit(success, message)

    def set_mode(self, mode: PatchWorkerMode):
        self.mode = mode

    def run(self):
        try:
            if self.mode == PatchWorkerMode.ALL:
                self._run_all()
            elif self.mode == PatchWorkerMode.EXTRACT:
                self._run_extract()
            elif self.mode == PatchWorkerMode.PATCH:
                self._run_patch()
            elif self.mode == PatchWorkerMode.COMPILE:
                self._run_compile()
        except Exception as exception:
            self._finish(False, f"Critical failure: {exception}")

    def _run_all(self):
        try:
            self._start(f"Extracting {self.filepath}...")
            self.patcher.extract(self.filepath)

            self._start("Patching the files with the activated mods...")
            self.patcher.apply_mods()

            self._start(f"Compiling to {self.outputpath}...")
            self.patcher.compile(self.outputpath)

            self._finish(True, "Game successfully patched !")
        except Exception as exception:
            self._finish(False, f"Error during patching process: {exception}")

    def _run_extract(self):
        try:
            self._start(f"Extracting {self.filepath}...")
            self.patcher.extract(self.filepath)
            self._finish(True, "Extraction done !")
        except Exception as exception:
            self._finish(False, f"Error during extraction process: {exception}")

    def _run_patch(self):
        try:
            self._start("Patching the files with the activated mods...")
            self.patcher.apply_mods()
            self._finish(True, "Mods applied !")
        except Exception as exception:
            self._finish(False, f"Error during patching process: {exception}")

    def _run_compile(self):
        try:
            self._start(f"Compiling to {self.outputpath}...")
            self.patcher.compile(self.outputpath)
            self._finish(True, "Compilation done !")
        except Exception as exception:
            self._finish(False, f"Error during compilation process: {exception}")
