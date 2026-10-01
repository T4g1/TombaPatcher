import struct
from pathlib import Path
from PIL import Image

# from game_parser.image import parse_img
from game_parser.vram import get_from_16bit_color, COLOR_SIZE

from common import (
    all,
    to_basepath,
    RLE_PATH,
    TIM_PATH,
)

TIM_SUFFIX = ".TIM"
TIM_HEADER = bytes.fromhex("10000000000000000100000000000000")

MAGIC_TIM = b"\x10\x00\x00\x00"


def generate_palette(bpp_mode: int) -> list[int]:
    palette = [0, 0, 0, 0]
    if bpp_mode == 0:
        for i in range(16 - 1):
            val = i << 4
            palette.extend([val, val, val, 255])
    else:
        for i in range(256 - 1):
            val = i >> 1
            palette.extend([val, val, val, 255])
    return palette


def to_clut_index(data: bytes, index: int, bpp_mode: int):
    if bpp_mode == 0:
        raw_byte = data[index // 2]
        return (raw_byte & 0x0F) if (index % 2 == 0) else ((raw_byte >> 4) & 0x0F)
    elif bpp_mode == 1:
        return data[index]
    else:
        return struct.unpack_from("<H", data, index * 2)[0]


def parse_img(data: bytes, width: int, height: int, bpp_mode: int, palette=None):
    if bpp_mode == 0:  # 4-bit (1 byte = 2 pixel)
        width = width * 4
    elif bpp_mode == 1:  # 8-bit
        width = width * 2

    total_pixels = width * height

    img = Image.new("P", (width, height))
    pixels = img.load()
    assert pixels

    if palette is None or len(palette) == 0:
        palette = generate_palette(bpp_mode)

    img.putpalette(palette, rawmode="RGBA")

    for i in range(total_pixels):
        x = i % width
        y = i // width

        clut_index = to_clut_index(data, i, bpp_mode)

        pixels[x, y] = clut_index

    return img


def tim_to_png(filepath: Path, outputpath: Path):
    """
    Parses a single TIM image from a binary data buffer at a given offset.
    Returns (Image object, total_bytes_consumed) or (None, 0) if invalid.
    """
    print(f"TIM: Extracting {filepath}...")

    with open(filepath, "rb") as f:
        data = f.read()

    tag, version, _, flags = struct.unpack_from("<BBHI", data)
    if tag != 0x10 or version != 0:
        return

    bpp_mode = flags & 0x03  # Bits 0-1: Bit depth mode
    clut_present = (flags >> 3) & 1  # Bit 3: CLUT presence flag

    current_ptr = 8
    palettes = []

    if clut_present:
        clut_length, clut_x, clut_y, clut_w, clut_h = struct.unpack_from(
            "<IHHHH", data, current_ptr
        )

        if clut_w > 200 or clut_h > 200:
            return

        if clut_w == 0 or clut_h == 0:
            return

        # The header includes the length word itself, so data size is length - 12
        clut_data_offset = current_ptr + 12

        for i in range(clut_w * clut_h):
            index = clut_data_offset + (i * COLOR_SIZE)
            raw_value = data[index : index + COLOR_SIZE]
            value = int.from_bytes(raw_value, byteorder="little")
            color = get_from_16bit_color(value)

            if color[3] == 0:
                palettes.append((0, 0, 0, 0))
            else:
                palettes.append((color[0], color[1], color[2], 255))

        current_ptr += clut_length

    img_length, img_x, img_y, width, height = struct.unpack_from(
        "<IHHHH", data, current_ptr
    )

    offset = current_ptr + 12

    img = parse_img(data[offset:], width, height, bpp_mode, palette=palettes)
    assert img

    img.save(outputpath)


def png_to_tim(filepath: Path, outputpath: Path):
    output = bytearray()
    output += TIM_HEADER

    img = Image.open(filepath)

    palette = img.getpalette(rawmode="RGBA")

    assert palette

    width = img.width
    height = img.height

    if len(palette) == 16 * 4:
        bpp_mode = 0
        pixel_per_byte = 2
        width = img.width // 4
    elif len(palette) == 256 * 4:
        bpp_mode = 1
        pixel_per_byte = 1
        width = img.width // 2
    else:
        raise ValueError("Unsupported image mode")

    output += struct.pack("<H", width)
    output += struct.pack("<H", height)

    total_bytes = img.width * img.height // pixel_per_byte
    bytes_per_line = img.width // pixel_per_byte

    # print(f"Size:({img.width}, {img.height}), bytes:{total_bytes}")

    for i in range(total_bytes):
        x = i % bytes_per_line * pixel_per_byte
        y = i // bytes_per_line

        if bpp_mode == 0:  # 4-bit indexed
            value_lower = img.getpixel((x, y))
            value_upper = img.getpixel((x + 1, y))

            assert isinstance(value_lower, int)
            assert isinstance(value_upper, int)

            value = (value_upper << 4) | value_lower
        else:  # bpp_mode == 2    # 8-bit indexed
            value = img.getpixel((x, y))

            assert isinstance(value, int)

        output += struct.pack("<B", value)

    with open(outputpath, "wb") as f:
        f.write(output)


def tim_to_png_all(source: Path, to: Path):
    for file in source.rglob(all(TIM_SUFFIX)):
        tim_to_png(file, to_basepath(file, to).with_suffix(".PNG"))


def png_to_tim_all(source: Path, to: Path):
    for file in source.rglob(all(".PNG")):
        png_to_tim(file, to_basepath(file, to).with_suffix(TIM_SUFFIX))


if __name__ == "__main__":
    tim_to_png_all(RLE_PATH, TIM_PATH)
