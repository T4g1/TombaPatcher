from pathlib import Path
import struct
from PIL import Image

from game_parser.ld import FileInfo, ld_load_all, ld_filter
from game_parser.fla import flas_load_with_lbas
from game_parser.vram import (
    get_grayscale_color,
    get_from_16bit_color,
    to_16bit_color,
    Pixel,
)
from game_parser.clut import load_clut

from common import (
    logger,
    all,
    to_basepath,
    is_matching,
    PNG_SUFFIX,
    IMG_PATH,
    LD_PATH,
    SYS_PATH,
    ENTRY_PATH,
    XML_PATH,
    ISO_PATH,
    GAM_PATH,
)

IMG_SUFFIX = ".1080"


def get_mode(filename: Path):
    if (
        "CLUT" in str(filename)
        or "A00001.0.10FF" in str(filename)
        or "A00002.0.10FF" in str(filename)
        or "A00004.0.10FF" in str(filename)
        or "A00005.0.10FF" in str(filename)
    ):
        return 2

    return 0


def parse_img(
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
        width = width * 4
    elif bpp_mode == 1:  # 8-bit
        width = width * 2
    elif bpp_mode == 2:  # 16-bit direct color (2 bytes = 1 pixel)
        width = width
    else:
        return None, 0

    total_pixels = width * height

    img = Image.new("RGBA", (width, height))
    pixels = img.load()
    assert pixels

    if bpp_mode == 0:  # 4-bit Indexed
        for index in range(total_pixels):
            byte_index = index // 2
            raw_byte = data[offset + byte_index]
            # Extract 4-bit nibbles
            clut_index = (
                (raw_byte & 0x0F) if (index % 2 == 0) else ((raw_byte >> 4) & 0x0F)
            )
            pixels[index % width, index // width] = get_color(
                bpp_mode, palette, clut_index
            )

    elif bpp_mode == 1:  # 8-bit Indexed
        for index in range(total_pixels):
            clut_index = data[offset + index]
            pixels[index % width, index // width] = get_color(
                bpp_mode, palette, clut_index
            )

    elif bpp_mode == 2:  # 16-bit Direct
        for index in range(total_pixels):
            color_raw = struct.unpack_from("<H", data, offset + index * 2)[0]
            pixels[index % width, index // width] = get_color(
                bpp_mode, palette, color_raw
            )

    return img, total_pixels


def extract_img(filepath: Path, outputpath: Path, width: int, height: int, mode: int):
    logger.info(f"IMG: Extracting {filepath} to {outputpath}...")
    with open(filepath, "rb") as f:
        data = f.read()

    img, _ = parse_img(data, width, height, mode)
    assert img

    img.save(outputpath)


def format_img(file: Path, to: Path):
    logger.info(f"IMG: Formating image {file} to {to}...")
    img = Image.open(file)

    output = bytes()
    for y in range(img.height):
        for x in range(img.width):
            color = img.getpixel((x, y))
            assert isinstance(color, tuple)

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

            output += struct.pack("<H", value)

    with open(to, "wb") as f:
        f.write(output)


def extract_all(files: list[FileInfo], to: Path):
    """List of files infos filtered or not"""
    for file in ld_filter(files, all(IMG_SUFFIX)):
        assert file.dest

        mode = 0
        if "CLUT" in file.dest.name:
            mode = 2

        # Adds two suffix
        output = to_basepath(file.dest, to).with_suffix(
            f"{file.dest.suffix}.mode{mode}{PNG_SUFFIX}"
        )
        extract_img(file.dest, output, file.width, file.height, mode)


def format_all(base: Path, to: Path, matching: list[str] = []):
    for file in base.rglob(all(PNG_SUFFIX)):
        if is_matching(file, matching):
            # Remove two suffix
            format_img(file, to_basepath(file, to).with_suffix("").with_suffix(""))


def extract_with_clut():
    # TODO: Clean this
    cluts = [
        ("CLUT01", 16, 16),
        ("CLUT02", 16, 16),
        ("CLUT03", 16, 16),
    ]

    filename = "B203.0.1080"

    for clut_spec in cluts:
        clut_name = clut_spec[0]
        clut_width = clut_spec[1]
        clut_height = clut_spec[2]

        clutpath = Path(f"output/img/AREA19/{clut_name}.0.mode2.PNG")

        filepath = Path(f"output/LD/AREA19/{filename}")
        with open(filepath, "rb") as f:
            data = f.read()

            for clut_x in range(clut_width):
                for clut_y in range(clut_height):
                    clut = load_clut(clutpath, clut_x * 16, clut_y, 0)

                    mode = 0
                    img, _ = parse_img(data, 192, 256, mode, palette=clut)
                    if img:
                        outputpath = Path(f"output/img/AREA19/{filename}.PNG")
                        outputpath = outputpath.with_suffix(
                            f".mode{mode}.clut-{clut_name}-{clut_x}-{clut_y}.PNG"
                        )
                        img.save(outputpath)


if __name__ == "__main__":
    flas = flas_load_with_lbas(ENTRY_PATH, XML_PATH)
    infos = ld_load_all(ISO_PATH, LD_PATH, SYS_PATH, flas, GAM_PATH)
    files = ld_filter(infos, all(IMG_SUFFIX))
    extract_all(files, IMG_PATH)
    format_all(IMG_PATH, LD_PATH)
