"""
Format:
Entries:
* Start: 4 bytes: Offset for start of data for this entry
* End: 4 bytes: Offset for end of data for this entry
Next entry: Each entry overlap 4 bytes on the previous one: So end of previous entry
is start of the next one
Stops when end is out of data
"""

from pathlib import Path

from common import read_int, to_basepath


def unpack(filepath: Path, basepath: Path) -> list[Path]:
    results = []

    with open(filepath, "rb") as f:
        data = f.read()

    entry_index = 0
    entry_count = read_int(data, 0, size=4)

    while entry_index < entry_count:
        offset = 4 + entry_index * 4

        data_start = read_int(data, offset, size=4)
        data_end = read_int(data, offset + 4, size=4)
        size = data_end - data_start

        outputpath = to_basepath(filepath, basepath).with_suffix(
            f"{filepath.suffix}.{entry_index}.UNPACK"
        )
        print(f"Unpacking {outputpath} of size: {size}...")

        with open(outputpath, "wb") as f:
            f.write(data[data_start:data_end])

        results.append(outputpath)
        entry_index += 1

    return results


if __name__ == "__main__":
    basepath = Path("output/processed/")
    outputpath = Path("output/unpack/")

    pattern = "*.5080"

    for path in basepath.rglob(pattern):
        print(f"Unpacking: {path}...")
        unpack(path, outputpath)
