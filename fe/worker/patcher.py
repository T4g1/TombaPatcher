from collections import defaultdict
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

    def run(self):
        """Given the path to a Tomba! bin/iso file:
        * Extracts the files from the ISO or BIN/CUE
        * Patch files
        * Construct the ISO or BIN/CUE back"""
        self.status_changed.emit("Extracting files...")
        unpack(self.filepath, self.extractpath)

        self.status_changed.emit("Applying Tomba! patches...")
        self.patch_files(Path(OUTPUT_FILES))

        self.status_changed.emit("Rebuilding files...")
        resultpath = pack(self.outputpath)

        self.status_changed.emit(f"Output: {str(resultpath)}")
        self.finished.emit(True, "Game successfully patched!")

    def filter_files(self, path: Path, pattern: str) -> list[Path]:
        """List all files in given directory that match given pattern"""
        return [file for file in path.rglob(pattern) if file.is_file()]

    def patch_files(self, path: Path):
        """Group commands by file and delegates patch application commands"""
        file_to_commands = defaultdict(list)

        for command in self.patch_commands:
            matching_files = self.filter_files(path, command.file_pattern)
            for target_file in matching_files:
                file_to_commands[target_file].append(command)

        for target_file, target_commands in file_to_commands.items():
            self.patch(target_file, target_commands)

    def patch(self, target_file: Path, commands: list[PatchCommand]):
        """Apply patch to given file"""
        self.status_changed.emit(f"Unpacking: {str(target_file)}...")
        unpacked = target_file.with_suffix(".BIN")
        gam_unpack(target_file, unpacked)

        self.status_changed.emit(f"Patching: {str(unpacked)}...")
        with open(unpacked, "r+b") as file:
            for command in commands:
                file.seek(command.address)
                file.write(command.data)

        self.status_changed.emit(f"Packing: {str(unpacked)}...")
        gam_pack(unpacked, target_file)
