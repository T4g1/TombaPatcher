from pathlib import Path

COMMAND_SIZE = 8


def decompress(filepath: Path, outputpath: Path):
    """
    Decompresses a RLE file and writes the uncompressed data to disk.
    """
    global log_index
    log_index = 0

    with open(filepath, "rb") as f:
        data = f.read()

    data_index = 0

    command_word = data[data_index]
    data_index += 1

    output = bytearray()
    output += bytes.fromhex("10000000000000000100000000000000")
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

    with open(outputpath, "wb") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    basepath = Path("output/packed")
    baseoutputpath = Path("output/rle")

    pattern = "*.RLE"
    for filepath in basepath.rglob(pattern):
        print(f"RLE: Decompressing {filepath}...")

        outputpath = baseoutputpath / filepath.parent.name
        outputpath.mkdir(parents=True, exist_ok=True)
        outputpath = outputpath / filepath.with_suffix(".TIM").name

        decompress(filepath, outputpath)
