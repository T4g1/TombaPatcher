import struct

from pathlib import Path


def unpack(filepath: Path):
    """
    Decompresses a GAM file and writes the uncompressed data to disk.
    """
    output_path = filepath.with_suffix(".bin")

    with open(filepath, "rb") as f:
        # Read header: magic, output_size, initial command_word
        magic = f.read(4)
        if magic != b"GAM\0":
            raise ValueError(f"Invalid file signature: {magic}")

        output_size = struct.unpack("<I", f.read(4))[0]
        command_word = struct.unpack("<H", f.read(2))[0]

        output = bytearray()
        bit_index = 0

        while len(output) < output_size:
            if bit_index == 16:
                cmd_bytes = f.read(2)
                if not cmd_bytes:
                    break  # Unexpected EOF before hitting output_size
                command_word = struct.unpack("<H", cmd_bytes)[0]
                bit_index = 0

            # Extract current bit from right to left
            bit = (command_word >> bit_index) & 1
            bit_index += 1

            if bit == 0:
                # Literal byte copy
                byte = f.read(1)
                if not byte:
                    break
                output.extend(byte)
            else:
                # Distance/Amount copy
                distance = int.from_bytes(f.read(1))
                amount = int.from_bytes(f.read(1))

                # Copy from previous output
                start_index = len(output) - distance
                for _ in range(amount):
                    if len(output) >= output_size:
                        break

                    output.append(output[start_index])

    with open(output_path, "wb") as output_file:
        output_file.write(output[:output_size])


def pack(filepath: str):
    pass


if __name__ == "__main__":
    unpack(Path("output/files/AREA00/CLUT01.GAM"))
