import struct
import fnmatch
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterator

from game_parser.gam import is_gam, UNGAM_SUFFIX

from common import (
    to_basepath,
    get_suffix_from_type,
    read_int,
    ISO_PATH,
    ENTRY_PATH,
    XML_PATH,
    SYS_PATH,
    GAM_PATH,
    LD_PATH,
)

from game_parser.fla import load_flas_with_lbas

LD_ENTRY_SIZE = 0x14

SIZE_FACTOR = 2


@dataclass
class FileInfo:
    # Which LD file holds this info
    ld_file: Path
    # Where this info is in the LD file
    ld_address: int

    index: int
    type: int
    ram_address: int
    size: int

    x: int = 0
    y: int = 0

    width: int = 0
    height: int = 0

    header: bytes = bytes()

    # From which file this is taken
    source: Path | None = None
    dest: Path | None = None

    # Increment for each file related to the same source
    count: int = 0

    def set_dest(self, to: Path) -> Path:
        """Where this particular file is extracted from LD informations"""
        if self.source is None:
            raise ValueError(
                "Cannot determine destination for this file info as it does not have a source path",
                self,
            )

        text_suffix = get_suffix_from_type(self.type)

        self.dest = to_basepath(self.source, to).with_suffix(
            f".{self.count}.{self.type:04X}{text_suffix}"
        )
        return self.dest


def group_by_file_index(files: list[FileInfo]) -> Iterator[list[FileInfo]]:
    """Yield list of files that are packed together in correct order"""
    last_file_start = -1
    for i in range(len(files)):
        file = files[i]
        if file.index != 0:
            if last_file_start != -1:
                yield files[last_file_start:i]

            last_file_start = i

    yield files[last_file_start:]


def ld_write(info: FileInfo):
    """Write back the FileInfo entry into the LD file"""
    with open(info.ld_file, "r+b") as f:
        f.seek(info.ld_address)

        f.write(info.header)
        f.write(struct.pack("<H", info.index))
        f.write(struct.pack("<H", info.type))
        f.write(struct.pack("<I", info.ram_address))
        f.write(struct.pack("<I", info.size))
        f.write(struct.pack("<I", 0))


def ld_load(filepath: Path) -> list[FileInfo]:
    print(f"LD: Loading {filepath}")

    files: list[FileInfo] = []

    with open(filepath, "rb") as f:
        entry = f.read(LD_ENTRY_SIZE)
        entry_address = 0
        while entry != bytes() and len(entry) == LD_ENTRY_SIZE:
            index = read_int(entry, 4, size=2)
            type = read_int(entry, 6, size=2)
            ram_address = read_int(entry, 8, size=4)
            x = read_int(entry, 0x0C, size=2)
            y = read_int(entry, 0x0E, size=2)
            width = read_int(entry, 0x10, size=2)
            height = read_int(entry, 0x12, size=2)

            size = read_int(entry, 0x0C, size=4)
            vram_check = read_int(entry, 0x10, size=4)
            if vram_check != 0:
                size = width * height * SIZE_FACTOR

            # Make sure the type is not an address
            if index != 0xFFFF and type & 0xFFF0 != 0x8000:
                files.append(
                    FileInfo(
                        filepath,
                        entry_address,
                        index,
                        type,
                        ram_address,
                        size,
                        x,
                        y,
                        width,
                        height,
                        entry[0:4],
                    )
                )

            entry = f.read(LD_ENTRY_SIZE)
            entry_address += LD_ENTRY_SIZE

    return files


def ld_load_all(
    base: Path,
    to: Path,
    sys_path: Path,
    entry_path: Path,
    xml_path: Path,
    gam_path: Path,
):
    flas = load_flas_with_lbas(entry_path, xml_path)
    loaded: list[FileInfo] = []

    count = 0
    filepath = flas[0].path

    for file in sys_path.rglob("LD*.BIN"):
        infos = ld_load(file)

        for info in infos:
            if info.index != 0:
                raw_path = flas[info.index].path
                assert raw_path

                count = 0
                filepath = base / raw_path
                if is_gam(filepath):
                    filepath = to_basepath(filepath, gam_path).with_suffix(UNGAM_SUFFIX)

            assert filepath
            info.source = base / filepath
            info.count = count
            info.set_dest(to)

            loaded.append(info)
            count += 1

    return loaded


def ld_filter(files: list[FileInfo], pattern: str) -> list[FileInfo]:
    """Pattern is like *.1080"""
    filtered = []
    for info in files:
        if info.dest is None:
            raise ValueError("File info has no dest path", info)
        if fnmatch.fnmatch(info.dest.name, pattern):
            filtered.append(info)
    return filtered


if __name__ == "__main__":
    files = ld_load_all(ISO_PATH, LD_PATH, SYS_PATH, ENTRY_PATH, XML_PATH, GAM_PATH)
    for file in files:
        print(
            f"0x{file.index:04X}: {file.source}\t{file.dest}\t\tType 0x{file.type:04X}, "
            f"RAM 0x{file.ram_address:08X}, Size 0x{file.size:08X} "
            f"(s: {file.size}, w: {file.width}; h: {file.height})"
        )
