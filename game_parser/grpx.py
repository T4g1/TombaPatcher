from pathlib import Path

from game_parser import Parser, consume_suffix, add_suffix
from game_parser.clut import load_clut
from game_parser.image import img_extract, img_format

from common import (
    PNG_SUFFIX,
    logger,
)

GRPX_SUFFIX = ".GRPX"


class GRPXParser(Parser):
    @staticmethod
    def forward(input: Path, params: dict[str, int] = {}) -> Path:
        width = params.get("width")
        height = params.get("height")

        if width is None or height is None:
            raise ValueError(f"GRPX: Missing width or height to extract {input}")

        mode = get_mode(input)

        output = consume_suffix(input)
        output = add_suffix(output, PNG_SUFFIX)

        grpx_extract(input, output, width, height, mode)

        return output

    @staticmethod
    def reverse(input: Path | list[Path], params: dict[str, int] = {}) -> Path:
        if isinstance(input, list):
            raise ValueError(
                "GRPX: Requires a single input path but got a list of files instead..."
            )

        output = consume_suffix(input)
        output = add_suffix(output, GRPX_SUFFIX)

        grpx_format(input, output)

        return output


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


def grpx_extract(filepath: Path, outputpath: Path, width: int, height: int, mode: int):
    logger.info(f"IMG: Extracting {filepath} to {outputpath}...")
    with open(filepath, "rb") as f:
        data = f.read()

    img, _ = img_extract(data, width, height, mode)
    assert img

    img.save(outputpath)


def grpx_format(filepath: Path, outputpath: Path):
    logger.info(f"IMG: Formating image {filepath} to {outputpath}...")

    data, _, _ = img_format(filepath)

    with open(outputpath, "wb") as f:
        f.write(data)


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
                    img, _ = img_extract(data, 192, 256, mode, palette=clut)
                    if img:
                        outputpath = Path(f"output/img/AREA19/{filename}.PNG")
                        outputpath = outputpath.with_suffix(
                            f".mode{mode}.clut-{clut_name}-{clut_x}-{clut_y}.PNG"
                        )
                        img.save(outputpath)
