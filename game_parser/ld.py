from pathlib import Path
from dataclasses import dataclass

from common import read_int

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


def load_ld(filepath: Path) -> list[FileInfo]:
    files: list[FileInfo] = []

    with open(filepath, "rb") as f:
        entry = f.read(LD_ENTRY_SIZE)
        while entry != bytes():
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

            if index != 0xFFFF and type >> 0x08 != 0x80:
                files.append(
                    FileInfo(
                        index, type, ram_address, size, x, y, width, height, entry[0:4]
                    )
                )

            entry = f.read(LD_ENTRY_SIZE)

    return files


if __name__ == "__main__":
    ld_directory = Path("output/files/SYS")

    all_types = []

    for filepath in ld_directory.rglob("*.BIN"):
        files = load_ld(filepath)

        for file in files:
            file_type = f"{file.type:04X}"
            if file_type not in all_types:
                all_types.append(file_type)
            print(
                f"0x{file.index:04X}: Type 0x{file.type:04X}, "
                f"RAM 0x{file.ram_address:08X}, Size 0x{file.size:08X} "
                f"(w: {file.width}; h: {file.height})"
            )

    print("All file type encountered:")
    for type in sorted(all_types):
        print(type)
