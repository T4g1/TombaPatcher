import enum

from dataclasses import dataclass

VRAM_HEIGHT = 512
BYTES_PER_LINE = 2048
BYTES_PER_PIXEL = 4
PAGE_WIDTH = 256
PAGE_HEIGHT = 256
PAGES_PER_LINE = 16

COLOR_SIZE = 2


class VRAMMode(enum.IntEnum):
    DIRECT_COLOR = 0
    CLUT_256 = 1
    CLUT_16 = 2


@dataclass
class Pixel:
    r: int
    g: int
    b: int
    a: int = 255


def get_from_16bit_color(value: int) -> Pixel:
    """Two bytes of data"""
    red = (value >> 0) & 0x1F
    green = (value >> 5) & 0x1F
    blue = (value >> 10) & 0x1F
    alpha = (value >> 15) & 0x01

    red = (red * 4) if red <= 15 else 64 + ((red - 16) * 12)
    green = (green * 4) if green <= 15 else 64 + ((green - 16) * 12)
    blue = (blue * 4) if blue <= 15 else 64 + ((blue - 16) * 12)
    alpha = 128 if alpha else 255

    if value == 0:
        # Prevents Pixmap from missing it
        alpha = 1

    return Pixel(red, green, blue, alpha)


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


def get_clut_value(data: bytearray, clut_address: int, color_index: int) -> Pixel:
    clut_value_index = clut_address + color_index * COLOR_SIZE
    value = int.from_bytes(
        data[clut_value_index : clut_value_index + COLOR_SIZE], byteorder="little"
    )
    return get_from_16bit_color(value)
