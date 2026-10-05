import struct
from pathlib import Path

from game_parser import Parser, consume_suffix, add_suffix

from common import (
    all,
    to_basepath,
    logger,
    is_matching,
)

GAM_SUFFIX = ".GAM"
UNGAM_SUFFIX = ".000"

MAGIC_GAM = b"GAM\0"

LZ_MIN_SIZE = 5

PAK_SUFFIX = ".PAK"


class GamParser(Parser):
    @staticmethod
    def forward(input: Path, params: dict[str, int] = {}) -> Path:
        output = consume_suffix(input)

        ungam(input, output)

        return output

    @staticmethod
    def reverse(input: Path | list[Path], params: dict[str, int] = {}) -> Path:
        if isinstance(input, list):
            raise ValueError(
                "GAM: Requires a single input path but got a list of files instead..."
            )

        output = add_suffix(input, GAM_SUFFIX)

        gam(input, output)

        return output


def is_gam(filepath: Path) -> bool:
    return filepath.suffix == GAM_SUFFIX


def ungam(input: Path, outputpath: Path):
    """
    Decompresses a GAM file and writes the uncompressed data to disk.
    """
    logger.info(f"GAM: Decompressing {input} to {outputpath}...")

    with open(input, "rb") as f:
        # Read header: magic, output_size, initial command_word
        magic = f.read(4)
        if magic != MAGIC_GAM:
            raise ValueError(f"Invalid file signature: {magic}")

        output_size = struct.unpack("<I", f.read(4))[0]
        command_word = struct.unpack("<H", f.read(2))[0]

        output = bytearray()
        command_index = 0

        while len(output) < output_size:
            if command_index == 16:
                cmd_bytes = f.read(2)
                if not cmd_bytes:
                    raise Exception("Unexpected EOF before hitting output_size")
                command_word = struct.unpack("<H", cmd_bytes)[0]
                command_index = 0

            # Extract current bit from right to left
            command = (command_word >> command_index) & 1
            command_index += 1

            if command == 0:
                # Literal byte copy
                byte = f.read(1)
                if not byte:
                    break

                output += byte

            else:
                # Distance/Amount copy
                distance = int.from_bytes(f.read(1))
                amount = int.from_bytes(f.read(1))

                byte_index = len(output) - distance

                for i in range(amount):
                    output.append(output[byte_index + i])

    with open(outputpath, "wb") as output_file:
        output_file.write(output[:output_size])


def gam(input: Path, outputpath: Path):
    logger.info(f"GAM: Compressing {input} to {outputpath}...")

    output = bytearray()

    with open(input, "rb") as f:
        data = f.read()

    i = 0
    while i < len(data):
        command_word = 0
        command_position = len(output)
        output += bytes(2)

        for command_index in range(16):
            offset, length = find_longest_chain(data, i)

            if length >= LZ_MIN_SIZE:
                # Chain copy
                command_word |= 1 << command_index
                output += struct.pack("<B", offset)
                output += struct.pack("<B", length)
                i += length

            else:
                # Direct copy
                output += data[i].to_bytes()
                i += 1

            if i >= len(data):
                break

        output[command_position : command_position + 2] = struct.pack(
            "<H", command_word
        )

    with open(outputpath, "wb") as output_file:
        output_file.write(MAGIC_GAM)
        output_file.write(struct.pack("<I", len(data)))
        output_file.write(output)


def find_longest_chain(data: bytes, at: int) -> tuple[int, int]:
    """
    Given a bytearray and a position in that bytearray:
    Search for a byte that can be repeated to represent the following bytes
    from the data after the given position.

    If no match is found, returns (0, 0).
    """
    best_offset = 0
    best_length = 0

    max_offset = min(255, at)

    for offset in range(1, max_offset + 1):
        offset_position = at - offset
        length = 0

        while (
            length < 255
            and offset_position + length < at
            and at + length < len(data)
            and data[offset_position + length] == data[at + length]
        ):
            length += 1

        if length > best_length:
            best_offset = offset
            best_length = length

    return best_offset, best_length


def ungam_all(base: Path, to: Path):
    for file in base.rglob(all(GAM_SUFFIX)):
        ungam(file, to_basepath(file, to).with_suffix(UNGAM_SUFFIX))


def gam_all(base: Path, to: Path, matching: list[str] = []):
    """Compress all files to GAM file
    Take an optional list of files that should be compressed"""
    for file in base.rglob(all(UNGAM_SUFFIX)):
        if is_matching(file, matching):
            gam(file, to_basepath(file, to).with_suffix(GAM_SUFFIX))
