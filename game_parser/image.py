import struct
import enum
from pathlib import Path
from PIL import Image

from dataclasses import dataclass

COLOR_SIZE = 2

GRAYSCALE = 10


class BPPMode(enum.IntEnum):
    DIRECT_COLOR = 0
    CLUT_256 = 1
    CLUT_16 = 2


@dataclass
class Pixel:
    r: int
    g: int
    b: int
    a: int = 255


def get_grayscale_color(value: int) -> tuple[int, int, int, int]:
    alpha = 255
    if value == 0:
        alpha = 0

    return (value, value, value, alpha)


def get_from_16bit_color(value: int) -> tuple[int, int, int, int]:
    """Two bytes of data"""
    red = (value >> 0) & 0x1F
    green = (value >> 5) & 0x1F
    blue = (value >> 10) & 0x1F
    alpha = (value >> 15) & 0x01

    red = (red * 4) if red <= 15 else 64 + ((red - 16) * 12)
    green = (green * 4) if green <= 15 else 64 + ((green - 16) * 12)
    blue = (blue * 4) if blue <= 15 else 64 + ((blue - 16) * 12)
    alpha = 128 if alpha else 255

    return (red, green, blue, alpha)


def to_16bit_color(pixel: Pixel) -> int:
    """Packs a Pixel into two bytes of data (16-bit color)"""
    if pixel.r == 0 and pixel.g == 0 and pixel.b == 0 and pixel.a == 1:
        return 0

    red = pixel.r // 4 if pixel.r <= 60 else ((pixel.r - 64) // 12) + 16
    green = pixel.g // 4 if pixel.g <= 60 else ((pixel.g - 64) // 12) + 16
    blue = pixel.b // 4 if pixel.b <= 60 else ((pixel.b - 64) // 12) + 16
    alpha = 1 if pixel.a == 128 else 0

    return (
        (red & 0x1F)
        | ((green & 0x1F) << 5)
        | ((blue & 0x1F) << 10)
        | ((alpha & 0x01) << 15)
    )


def generate_palette(bpp_mode: int) -> list[int]:
    """Generate a grayscale palette for the given mode"""
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


def img_extract(
    data: bytes, width: int, height: int, bpp_mode: int, offset: int = 0, palette=None
):
    def get_color(mode: int, clut, value: int):
        if clut is None or len(clut) == 0:
            if mode == 0:
                return get_grayscale_color(value << 4)
            elif mode == 1:
                return get_grayscale_color(value >> 1)
            else:
                return get_from_16bit_color(color_raw)

        return clut[value]

    if bpp_mode == 0:  # 4-bit (1 byte = 2 pixel)
        img_type = "P"
        width = width * 4
    elif bpp_mode == 1:  # 8-bit
        img_type = "P"
        width = width * 2
    elif bpp_mode == 2:  # 16-bit direct color (2 bytes = 1 pixel)
        img_type = "RGBA"
        width = width
    else:
        return None, 0

    total_pixels = width * height

    img = Image.new(img_type, (width, height))
    pixels = img.load()
    assert pixels

    if palette is None or len(palette) == 0:
        palette = generate_palette(bpp_mode)

    if bpp_mode != 2:
        img.putpalette(palette, rawmode="RGBA")

    for index in range(total_pixels):
        x = index % width
        y = index // width

        if bpp_mode == 0:  # 4-bit Indexed
            raw_byte = data[offset + index // 2]
            clut_index = (
                (raw_byte & 0x0F) if (index % 2 == 0) else ((raw_byte >> 4) & 0x0F)
            )
            pixels[x, y] = clut_index

        elif bpp_mode == 1:  # 8-bit Indexed
            clut_index = data[offset + index]
            pixels[x, y] = clut_index

        elif bpp_mode == 2:  # 16-bit Direct
            color_raw = struct.unpack_from("<H", data, offset + index * COLOR_SIZE)[0]
            pixels[x, y] = get_from_16bit_color(color_raw)

    return img, total_pixels


def img_format(filepath: Path) -> tuple[bytearray, int, int]:
    img = Image.open(filepath)

    width = img.width
    height = img.height

    palette = img.getpalette(rawmode="RGBA")
    if palette is None:  # 16-bit color
        bpp_mode = 2
        width = img.width
        bytes_per_pixel = 2
    elif len(palette) == 256 * 4:  # 8-bit color
        bpp_mode = 1
        width = img.width // 2
        bytes_per_pixel = 1
    elif len(palette) == 16 * 4:  # 4-bit color
        bpp_mode = 0
        width = img.width // 4
        bytes_per_pixel = 0.5

        if img.width % 2 != 0:
            raise ValueError(
                f"Trying to format an image with a width that is not a multiple of 2: {img.width}"
            )
    else:
        raise AttributeError(
            f"Unexpected image palette size for {filepath}: {len(palette)}"
        )

    bytes_per_line = int(img.width * bytes_per_pixel)
    total_bytes = bytes_per_line * img.height

    data = bytearray(total_bytes)
    for y in range(img.height):
        for x in range(img.width):
            color = img.getpixel((x, y))

            if bpp_mode == 0:  # 4-bit palette index
                if not isinstance(color, int):
                    raise ValueError(f"Got a color that is not an index: {color}")

                byte_index = y * bytes_per_line + (x // 2)
                if x % 2 == 0:
                    data[byte_index] |= color & 0x0F
                else:
                    data[byte_index] |= (color & 0x0F) << 4

            elif bpp_mode == 1:  # 8-bit palette index
                if not isinstance(color, int):
                    raise ValueError(f"Got a color that is not an index: {color}")

                byte_index = y * bytes_per_line + x
                data[byte_index] &= 0x12

            else:  # 16-bit color
                if not isinstance(color, tuple):
                    raise ValueError(
                        f"Got an unsupported color for 16-bit color image: {color}"
                    )

                byte_index = y * bytes_per_line + (x * 2)
                if len(color) == 2:
                    # Grayscale, Alpha
                    value = to_16bit_color(
                        Pixel(
                            color[0],
                            color[0],
                            color[0],
                            color[1],
                        )
                    )
                else:
                    value = to_16bit_color(
                        Pixel(
                            color[0],
                            color[1],
                            color[2],
                            color[3] if len(color) > 3 else 255,
                        )
                    )

                data[byte_index] = value & 0xFF
                data[byte_index + 1] = (value >> 8) & 0xFF

    return data, width, height
