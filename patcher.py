from PySide6.QtCore import QThread, Signal
from pathlib import Path

from game_parser.mkpsxiso import unpack, pack

OUTPUT_FILES = "output/files"


class PatchWorker(QThread):
    status_changed = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, filepath: str):
        super().__init__()

        self.filepath = Path(filepath)
        self.extractpath = Path(OUTPUT_FILES)
        self.outputpath = (
            self.filepath.parent / f"{self.filepath.stem}.patched{self.filepath.suffix}"
        )

    def run(self):
        self.status_changed.emit("Extracting files...")
        unpack(self.filepath, self.extractpath)

        self.status_changed.emit("Applying Tomba! patches...")
        self.patch_files(Path(OUTPUT_FILES))

        self.status_changed.emit("Rebuilding files...")
        pack(self.outputpath)

        self.finished.emit(True, "Game successfully patched!")

    def patch_files(self, path: Path):
        """Given the path to a Tomba! bin/iso file:
        * Extracts the files from the ISO
        * Patch files
        * Construct the ISO back"""
        # TODO
        return ""
