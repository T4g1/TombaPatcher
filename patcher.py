from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal
from pathlib import Path

from game_parser.mkpsxiso import unpack, pack
from game_parser.gam import unpack as gam_unpack, pack as gam_pack

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
        self.extractpath = Path(OUTPUT_FILES)
        self.outputpath = (
            self.filepath.parent / f"{self.filepath.stem}.patched{self.filepath.suffix}"
        )

        self.patch_commands = patches
        # self.patch_commands = [
        #     PatchCommand(
        #         "CLUT*.GAM",
        #         0x0002,
        #         bytes.fromhex("491C491C491C491C491C491C491C491C491C491C491C")
        #     )
        # ]

    def run(self):
        """Given the path to a Tomba! bin/iso file:
        * Extracts the files from the ISO or BIN/CUE
        * Patch files
        * Construct the ISO or BIN/CUE back"""
        self.status_changed.emit("Extracting files...")
        unpack(self.filepath, self.extractpath)

        self.status_changed.emit("Applying Tomba! patches...")
        for patch_command in self.patch_commands:
            self.patch_files(Path(OUTPUT_FILES), patch_command)

        self.status_changed.emit("Rebuilding files...")
        resultpath = pack(self.outputpath)

        self.status_changed.emit(f"Output: {str(resultpath)}")
        self.finished.emit(True, "Game successfully patched!")

    def patch_files(self, path: Path, command: PatchCommand):
        """Apply a patch command"""
        for file in self.filter_files(path, command.file_pattern):
            self.patch(file, command.address, command.data)

    def filter_files(self, path: Path, pattern: str) -> list[Path]:
        """List all files in given directory that match given pattern"""
        return [file for file in path.rglob(pattern) if file.is_file()]

    def patch(self, target_file: Path, address: int, data: bytes):
        """Apply patch to given file"""
        self.status_changed.emit(f"Unpacking: {str(target_file)}...")
        unpacked = target_file.with_suffix(".BIN")
        gam_unpack(target_file, unpacked)

        self.status_changed.emit(f"Patching: {str(unpacked)}...")
        with open(unpacked, "r+b") as file:
            file.seek(address)
            file.write(data)

        self.status_changed.emit(f"Packing: {str(unpacked)}...")
        gam_pack(unpacked, target_file)
