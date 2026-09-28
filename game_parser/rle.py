from pathlib import Path
from common import read_int

COMMAND_SIZE = 8


def unpack(filepath: Path, offset: int, size: int, outputpath: Path | None = None):
    """
    Decompresses a RLE file and writes the uncompressed data to disk.
    """
    global log_index
    log_index = 0

    if outputpath is None:
        outputpath = filepath.with_suffix(".bin")

    with open(filepath, "rb") as f:
        data = f.read()

    data_index = offset

    command_word = data[data_index]
    data_index += 1

    output = bytearray()
    output += bytes.fromhex("10000000000000000100000000000000")
    command_index = 0

    while data_index < offset + size:
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

    with open(outputpath, "wb") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    basepath = Path("output/processed")
    pattern = "*.RLE"
    for path in basepath.rglob(pattern):
        print(f"Unpacking: {path}...")

        with open(path, "rb") as f:
            data = f.read()

        frame_count = read_int(data, 0, size=4)
        for frame_index in range(frame_count + 1):
            offset = frame_index * 4

            data_start = read_int(data, offset, size=4)
            data_end = read_int(data, offset + 4, size=4)
            size = data_end - data_start

            try:
                unpack(
                    path,
                    data_start,
                    data_end - data_start,
                    path.with_suffix(f".RLE.{frame_index}.TIM"),
                )
            except Exception:
                print(
                    f"Skipped {path}: Does not seem to be a RLE compressed TIM file..."
                )
                break
