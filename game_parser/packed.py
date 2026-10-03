"""
Format:
Header:
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

from game_parser.rle import RLE_SUFFIX

from common import (
    logger,
    all,
    read_int,
    to_basepath,
    LD_PATH,
    PACKED_PATH,
)

PACKED_SUFFIX = ".PAK"


def get_path_packed(base: Path) -> Path:
    return base / "pak"


def unpack(filepath: Path, basepath: Path) -> list[Path]:
    """Unpacking file to a given directory"""
    logger.info(f"Packed: Unpacking {filepath}...")

    results = []

    with open(filepath, "rb") as f:
        data = f.read()

    entry_index = 0

    entry_count = read_int(data, 0, size=4)

    first_offset = read_int(data, 4, size=4)

    # End is sometimes at -3, sometimes -1...
    end_threshold = len(data) - 3

    offset = 4
    while offset < first_offset:
        data_start = read_int(data, offset, size=4)
        data_end = len(data)
        if offset + 4 < first_offset:
            data_end = read_int(data, offset + 4, size=4)

        if data_start >= end_threshold:
            assert entry_index == entry_count
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

        suffix = Path(filepath.stem).suffix
        base_stem = Path(filepath.stem).stem

        outputpath = to_basepath(filepath, basepath).with_name(
            f"{base_stem}.{entry_index:04X}{suffix}"
        )
        logger.info(f"Unpacking {outputpath} of size: {size}...")

        with open(outputpath, "wb") as f:
            f.write(data[data_start:data_end])

        results.append(outputpath)
        entry_index += 1
        offset = 4 + entry_index * 4

    return results


def pack(inputdirectory: Path, outputpath: Path):
    """Packing file in a given directory to a given path
    Packed files must match the pattern implied by the output filename"""
    logger.info(f"Packed: Re-packing to {outputpath}...")

    suffix = Path(outputpath.stem).suffix
    base_stem = Path(outputpath.stem).stem

    pattern = f"{outputpath.parent.name}/{base_stem}.*{suffix}"

    # 5080 files does not have the last entry being the EOF address
    with_eof = suffix != ".5080"

    # Ordering is important: This assumes the list is ordered by hexadecimal suffixes
    # ie: 0001.x is before 000A.x
    unpacked_filepaths = [path for path in inputdirectory.rglob(pattern)]

    entry_count = len(unpacked_filepaths)

    with open(outputpath, "wb") as output:
        # Write file count
        output.write(struct.pack("<I", entry_count))

        # Write file offsets
        offset = 4 + entry_count * 4
        if with_eof:
            offset += 4

        for unpacked_path in unpacked_filepaths:
            output.write(struct.pack("<I", offset))
            offset += os.path.getsize(unpacked_path)

        if with_eof:
            output.write(struct.pack("<I", offset))

        # Write files
        for unpacked_path in unpacked_filepaths:
            with open(unpacked_path, "rb") as f:
                output.write(f.read())


def unpack_all(source: Path, to: Path) -> set[Path]:
    """Unpack all file with .PAK in source to given to
    Returns list of packed files processed"""
    files = set()
    for file in source.rglob(all(PACKED_SUFFIX)):
        unpack(file, to)
        files.add(file)
    return files


def pack_all(source: Path, to: Path):
    rle_files = [file for file in source.rglob(all(RLE_SUFFIX))]

    # Build list of files from the extracted ones
    files = set()
    for file in rle_files:
        parts = file.name.split(".")
        cleaned_parts = parts[:-2] + [parts[-1]]

        new_name = ".".join(cleaned_parts) + PACKED_SUFFIX
        files.add(file.parent / new_name)

    pack_all_files(source, to, files)


def pack_all_files(source: Path, to: Path, files: set[Path]):
    """Same as pack but with explicit list of files"""
    for file in files:
        pack(source, to_basepath(file, to))


if __name__ == "__main__":
    unpack_all(LD_PATH, PACKED_PATH)
