import struct
from pathlib import Path

from game_parser import Parser, consume_suffix, add_suffix
from game_parser.image import (
    COLOR_SIZE,
    get_from_16bit_color,
    img_extract,
    img_format,
)

from common import (
    PNG_SUFFIX,
    logger,
)

TIM_SUFFIX = ".TIM"
TIM_HEADER = bytes.fromhex("10000000000000000100000000000000")

MAGIC_TIM = b"\x10\x00\x00\x00"


class TIMParser(Parser):
    @staticmethod
    def forward(input: Path, params: dict[str, int] = {}) -> Path:
        output = consume_suffix(input)
        output = add_suffix(output, PNG_SUFFIX)

        tim_to_png(input, output)

        return output

    @staticmethod
    def reverse(input: Path | list[Path], params: dict[str, int] = {}) -> Path:
        if isinstance(input, list):
            raise ValueError(
                "TIM: Requires a single input path but got a list of files instead..."
            )

        output = consume_suffix(input)
        output = add_suffix(output, TIM_SUFFIX)

        png_to_tim(input, output)

        return output


def tim_to_png(filepath: Path, outputpath: Path):
    """
    Parses a single TIM image from a binary data buffer at a given offset.
    Returns (Image object, total_bytes_consumed) or (None, 0) if invalid.
    """

    logger.info(f"TIM: Extracting {filepath} to {outputpath}...")

    with open(filepath, "rb") as f:
        data = f.read()

    tag, version, _, flags = struct.unpack_from("<BBHI", data)
    if tag != 0x10 or version != 0:
        raise ValueError(f"TIM: Header is wrong: tag:{tag:02X} version:{version:02X}")

    bpp_mode = flags & 0x03  # Bits 0-1: Bit depth mode
    clut_present = (flags >> 3) & 1  # Bit 3: CLUT presence flag

    current_ptr = 8
    palettes = []

    if clut_present:
        clut_length, clut_x, clut_y, clut_w, clut_h = struct.unpack_from(
            "<IHHHH", data, current_ptr
        )

        if clut_w > 200 or clut_h > 200 or clut_w == 0 or clut_h == 0:
            raise ValueError(f"TIM: Got CLUT with a unexpected size: {clut_w}x{clut_h}")

        # The header includes the length word itself, so data size is length - 12
        clut_data_offset = current_ptr + 12

        for i in range(clut_w * clut_h):
            index = clut_data_offset + (i * COLOR_SIZE)
            raw_value = data[index : index + COLOR_SIZE]
            value = int.from_bytes(raw_value, byteorder="little")
            color = get_from_16bit_color(value)

            if color[3] == 0:
                palettes.extend((0, 0, 0, 0))
            else:
                palettes.extend((color[0], color[1], color[2], 255))

        current_ptr += clut_length

    img_length, img_x, img_y, width, height = struct.unpack_from(
        "<IHHHH", data, current_ptr
    )

    offset = current_ptr + 12

    img, _ = img_extract(data[offset:], width, height, bpp_mode, palette=palettes)
    assert img

    img.save(outputpath)


def png_to_tim(filepath: Path, outputpath: Path):
    logger.info(f"TIM: PNG {filepath} to TIM {outputpath}...")

    data, width, height = img_format(filepath)

    # TODO: Handle CLUT data and HEADER
    output = bytearray()
    output += TIM_HEADER
    output += struct.pack("<H", width)
    output += struct.pack("<H", height)

    with open(outputpath, "wb") as f:
        f.write(output)
        f.write(data)
