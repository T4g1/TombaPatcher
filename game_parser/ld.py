from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterator

from common import (
    read_int,
    ENTRY_PATH,
    XML_PATH,
    SYS_PATH,
)

from game_parser.fla import load_flas_with_lbas

LD_ENTRY_SIZE = 0x14

SIZE_FACTOR = 2


@dataclass
class FileInfo:
    index: int
    type: int
    ram_address: int
    size: int

    x: int = 0
    y: int = 0

    width: int = 0
    height: int = 0

    header: bytes = bytes()


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


def load_ld(filepath: Path) -> list[FileInfo]:
    print(f"LD: Loading {filepath}")

    files: list[FileInfo] = []

    with open(filepath, "rb") as f:
        entry = f.read(LD_ENTRY_SIZE)
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
                        index, type, ram_address, size, x, y, width, height, entry[0:4]
                    )
                )

            entry = f.read(LD_ENTRY_SIZE)

    return files


if __name__ == "__main__":
    all_types = []

    flas = load_flas_with_lbas(ENTRY_PATH, XML_PATH)

    filepath = flas[0].path

    for filepath in SYS_PATH.rglob("LD*.BIN"):
        files = load_ld(filepath)

        for file in files:
            file_type = f"{file.type:04X}"
            if file_type not in all_types:
                all_types.append(file_type)

            if file.index != 0:
                filepath = flas[file.index].path

            print(
                f"0x{file.index:04X}: {filepath}\t\tType 0x{file.type:04X}, "
                f"RAM 0x{file.ram_address:08X}, Size 0x{file.size:08X} "
                f"(s: {file.size}, w: {file.width}; h: {file.height})"
            )

    print("All file type encountered:")
    for type in sorted(all_types):
        print(type, end=", ")
