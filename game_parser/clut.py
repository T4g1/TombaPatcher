from PIL import Image
from pathlib import Path


def load_clut(
    filepath: Path, x: int, y: int, mode: int
) -> list[tuple[int, int, int, int]]:
    clut: list[tuple[int, int, int, int]] = []

    clut_size = 16
    if mode == 1:
        clut_size = 256

    with Image.open(filepath) as img:
        pixels = img.load()
        assert pixels

        for i in range(clut_size):
            pixel = pixels[x + i, y]

            assert isinstance(pixel, tuple)
            assert len(pixel) >= 4

            rgba_pixel = (pixel[0], pixel[1], pixel[2], pixel[3])

            clut.append(rgba_pixel)

    return clut
