"""
Format:
Header: (absent for 63FF files)
* Count: 4 bytes: Amount of entry packed

Entries:
* Start: 4 bytes: Offset for start of data for this entry
* End: 4 bytes: Offset for end of data for this entry

Next entry: Each entry overlap 4 bytes on the previous one: So end of previous entry
is start of the next one except for the last entry whose data end is the size of the file

Stops when last entry is reached
"""

import os
import struct
from pathlib import Path

from game_parser import Parser, consume_suffix, consume_token, add_suffix, add_token

from common import (
    logger,
    read_int,
    to_basepath,
)

PAK_SUFFIX = ".PAK"


class PackedParser(Parser):
    @staticmethod
    def forward(input: Path, params: dict[str, int] = {}) -> list[Path]:
        return unpack(input)

    @staticmethod
    def reverse(files: Path | list[Path], params: dict[str, int] = {}) -> Path:
        if isinstance(files, Path):
            raise ValueError(
                f"PAK: Requires a list of files to be packed but got {input} instead"
            )

        output = files[0]
        output = consume_token(output)
        output = add_suffix(output, PAK_SUFFIX)

        pack(files, output)

        return output


def unpack(filepath: Path, basepath: Path | None = None) -> list[Path]:
    """Unpacking file to a given directory"""
    logger.info(f"Packed: Unpacking {filepath}...")

    results = []

    with open(filepath, "rb") as f:
        data = f.read()

    entry_index = 0
    offset = 4

    entry_count = read_int(data, 0, size=4)
    first_offset = read_int(data, 4, size=4)

    if ".63FF" in str(filepath):
        first_offset = entry_count
        entry_count = -1  # Unknown
        offset = 0

    # End is sometimes at -3, sometimes -1...
    end_threshold = len(data) - 3

    while offset < first_offset:
        data_start = read_int(data, offset, size=4)
        data_end = len(data)
        if offset + 4 < first_offset:
            data_end = read_int(data, offset + 4, size=4)

        if data_start >= end_threshold:
            if ".63FF":
                entry_count = entry_index + 1

            assert (
                entry_index + 1 == entry_count
            ), "Reached end of the address table but entry count do not match"
            break

        if data_end >= end_threshold:
            data_end = len(data)

        size = data_end - data_start

        if data_start > len(data):
            raise ValueError(
                f"Found data start {data_start:08X} higher than data size {len(data)}"
            )

        if size <= 0:
            raise ValueError(
                f"Invalid size with {entry_index}: {data_start:08X} to {data_end:08X}"
            )

        if basepath:
            outputpath = to_basepath(filepath, basepath)
        else:
            outputpath = filepath.parent / filepath.name

        outputpath = consume_suffix(filepath)
        outputpath = add_token(outputpath, f"{entry_index:04X}")

        logger.info(f"Unpacking {outputpath} of size: {size}...")

        with open(outputpath, "wb") as f:
            f.write(data[data_start:data_end])

        results.append(outputpath)
        entry_index += 1
        offset += 4

    return results


def pack(files: list[Path], outputpath: Path):
    """Pack a list of files"""
    logger.info(f"PAK: Re-packing to {outputpath}...")

    # 5080 files does not have the last entry being the EOF address
    with_eof = ".5080" not in outputpath.suffixes

    entry_count = len(files)

    with open(outputpath, "wb") as output:
        # Write file count
        output.write(struct.pack("<I", entry_count))

        # Write file offsets
        offset = 4 + entry_count * 4
        if with_eof:
            offset += 4

        for unpacked_path in files:
            output.write(struct.pack("<I", offset))
            offset += os.path.getsize(unpacked_path)

        if with_eof:
            output.write(struct.pack("<I", offset))

        # Write files
        for unpacked_path in files:
            with open(unpacked_path, "rb") as f:
                output.write(f.read())
