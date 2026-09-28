from pathlib import Path
from dataclasses import dataclass

from common import bcd_to_int

FLA_ADDRESS = 0x0699A0
FLA_ENTRY_COUNT = 0x41E
FLA_ENTRY_SIZE = 0x08


@dataclass
class FLA:
    index: int
    lba: int
    size: int
    path: str | None = None


def load_flas(mainpath: Path) -> dict[int, FLA]:
    flas: dict[int, FLA] = {}

    with open(mainpath, "rb") as f:
        data = f.read()

    index = 0
    while index < FLA_ENTRY_COUNT:
        cursor = FLA_ADDRESS + index * FLA_ENTRY_SIZE
        fla_raw = data[cursor : cursor + FLA_ENTRY_SIZE]

        minute = bcd_to_int(fla_raw[0])
        second = bcd_to_int(fla_raw[1])
        sector = bcd_to_int(fla_raw[2])

        lba = ((minute * 60) + second) * 75 + sector - 150
        size = int.from_bytes(fla_raw[4:], byteorder="little")

        flas[index] = FLA(index, lba, size)

        index += 1

    return flas


if __name__ == "__main__":
    mainpath = Path("output/files/SCUS_942.36")
    flas = load_flas(mainpath)

    for index, fla in flas.items():
        print(f"0x{index:04X}: {fla.lba}\t{fla.size}")
