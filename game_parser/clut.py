from pathlib import Path

from PySide6.QtGui import QImage

from vram import (
    Pixel,
    VRAMMode,
    BYTES_PER_PIXEL,
    BYTES_PER_LINE,
    COLOR_SIZE,
    get_from_16bit_color,
)


def add_pixel(pixels: bytearray, pixel: Pixel) -> bytearray:
    pixels += pixel.r.to_bytes()
    pixels += pixel.g.to_bytes()
    pixels += pixel.b.to_bytes()
    pixels += pixel.a.to_bytes()
    return pixels


def extract_img(filepath: Path):
    output_path = filepath.with_suffix(".png")

    with open(filepath, "rb") as input_file:
        data = input_file.read()

    mode = VRAMMode.DIRECT_COLOR
    width = 1024
    if mode is VRAMMode.CLUT_256:
        width = 2048
    elif mode is VRAMMode.CLUT_16:
        width = 4096
    height = 10

    pixels: bytearray = bytearray()
    for y in range(height):
        for x in range(width):
            index = (y * BYTES_PER_LINE) + x * COLOR_SIZE
            if index > len(data):
                break

            raw_value = data[index : index + COLOR_SIZE]
            pixel = get_from_16bit_color(int.from_bytes(raw_value, byteorder="little"))
            pixels = add_pixel(pixels, pixel)

    image = QImage(
        pixels,
        width,
        height,
        width * BYTES_PER_PIXEL,
        QImage.Format.Format_RGBA8888,
    )
    image.save(str(output_path))


if __name__ == "__main__":
    extract_img(Path("output/files/AREA00/CLUT01.bin"))
