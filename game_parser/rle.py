from pathlib import Path

from game_parser.tim import TIM_SUFFIX, TIM_HEADER

from common import (
    all,
    to_basepath,
    RLE_PATH,
    PACKED_PATH,
)

RLE_SUFFIX = ".RLE"

COMMAND_SIZE = 8


def decompress(filepath: Path, outputpath: Path):
    """
    Decompresses a RLE file and writes the uncompressed data to disk.
    """
    print(f"RLE: Decompressing {filepath}...")

    with open(filepath, "rb") as f:
        data = f.read()

    data_index = 0

    command_word = data[data_index]
    data_index += 1

    output = bytearray()
    output += TIM_HEADER
    command_index = 0

    while data_index < len(data):
        if command_index == COMMAND_SIZE:
            command_word = data[data_index]
            data_index += 1
            command_index = 0

        # Extract current bit from right to left
        command = (command_word >> command_index) & 1
        command_index += 1

        if command == 0:
            # Literal byte copy
            byte = data[data_index].to_bytes()
            if not byte:
                break

            data_index += 1
            output += byte

        else:
            # Amount/Value copy
            amount = data[data_index]
            value = data[data_index + 1].to_bytes()

            data_index += 2
            for _ in range(amount):
                output += value
    print(outputpath)
    with open(outputpath, "wb") as output_file:
        output_file.write(output)


def compress(filepath: Path, outputpath: Path):
    print(f"RLE: Compressing {filepath}...")

    with open(filepath, "rb") as f:
        f.seek(len(TIM_HEADER))
        data = f.read()

    output = bytearray()

    # Placeholders to buffer up to 8 commands/data blocks at a time
    pending_flags = []
    pending_data = bytearray()

    data_index = 0
    data_len = len(data)

    while data_index < data_len:
        current_byte = data[data_index]

        # Count consecutive matching bytes (up to a maximum of 255)
        run_length = 0
        while (
            data_index + run_length < data_len
            and data[data_index + run_length] == current_byte
            and run_length < 255
        ):
            run_length += 1

        # Determine if it's more efficient to use an amount/value copy
        if run_length > 1:
            pending_flags.append(1)
            pending_data.append(run_length)
            pending_data.append(current_byte)
            data_index += run_length
        else:
            pending_flags.append(0)
            pending_data.append(current_byte)
            data_index += 1

        if len(pending_flags) == COMMAND_SIZE:
            command_word = 0
            # Construct the command word from right to left (LSB to MSB)
            for i, flag in enumerate(pending_flags):
                command_word |= flag << i

            output.append(command_word)
            output.extend(pending_data)

            pending_flags.clear()
            pending_data.clear()

    if pending_flags:
        command_word = 0
        for i, flag in enumerate(pending_flags):
            command_word |= flag << i

        output.append(command_word)
        output.extend(pending_data)

    with open(outputpath, "wb") as output_file:
        output_file.write(output)


def decompress_all(source: Path, to: Path) -> set[Path]:
    files = set()
    for file in source.rglob(all(RLE_SUFFIX)):
        decompress(file, to_basepath(file, to).with_suffix(TIM_SUFFIX))
        files.add(file)
    return files


def compress_all(source: Path, to: Path):
    for file in source.rglob(all(TIM_SUFFIX)):
        compress(file, to_basepath(file, to).with_suffix(RLE_SUFFIX))


if __name__ == "__main__":
    decompress_all(PACKED_PATH, RLE_PATH)
