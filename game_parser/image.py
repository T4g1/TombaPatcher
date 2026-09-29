from pathlib import Path
import struct
from PIL import Image

from game_parser.fla import load_flas_with_lbas
from game_parser.ld import load_ld
from game_parser.files import get_suffix
from game_parser.vram import get_grayscale_color, get_from_16bit_color


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
        height = height // 2
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
    with open(filepath, "rb") as f:
        data = f.read()

    img, _ = parse_img(data, width, height, mode)
    if img:
        outputpath = outputpath.with_suffix(f".mode{mode}.PNG")
        img.save(outputpath)
        print(f"Extracted image to {outputpath}")


if __name__ == "__main__":
    pattern = "1080"
    basepath = Path("output/files")

    xmlpath = Path("output/tomba.xml")
    mainpath = basepath / "SCUS_942.36"
    flas = load_flas_with_lbas(mainpath, xmlpath)

    syspath = basepath / "SYS"
    for ldpath in syspath.rglob("LDSYS.BIN"):
        print(f"Load LD: {ldpath}...")
        files = load_ld(ldpath)

        filepath: Path | None = None
        offset: int = 0
        file_count: int = 0
        for file in files:
            if file.index != 0:
                offset = 0
                file_count = 0
                fla = flas[file.index]

                assert fla.path
                filepath = basepath / fla.path

                if filepath.suffix == ".GAM":
                    unpackedpath = Path("output/unpacked") / filepath.parent.name
                    unpackedpath.mkdir(parents=True, exist_ok=True)
                    unpackedpath = unpackedpath / filepath.name

                    filepath = unpackedpath

            assert filepath

            type_suffix = f"{file.type:04X}"
            text_suffix = get_suffix(type_suffix)

            processedpath = Path("output/processed") / filepath.parent.name
            processedpath.mkdir(parents=True, exist_ok=True)
            processedpath = (
                processedpath
                / filepath.with_suffix(f".{file_count}.{text_suffix}").name
            )

            if file.width > 0 and file.height > 0:
                outputpath = Path("output/images") / processedpath.parent.name
                outputpath.mkdir(parents=True, exist_ok=True)
                outputpath = outputpath / processedpath.with_suffix(".PNG").name

                print(f"Extracting {processedpath} to {outputpath}...")

                mode = get_mode(processedpath)

                if file.height == 1:
                    file.height = 2
                    mode = 2

                print(
                    f"Parameters: w:{file.width}, h:{file.height}, mode:{mode} - x:0x{file.x:04X}, y:0x{file.y:04X}, header:{file.header.hex()}"
                )
                extract_img(processedpath, outputpath, file.width, file.height, mode)

            file_count += 1
            offset += file.size

    # cluts = [
    #     ("A00001", 1, 8),
    #     ("A00002", 1, 2),
    #     ("DSPCLUT", 3, 15),
    # ]

    # filename = "A00014.0.10FF"

    # for clut_spec in cluts:
    #     clut_name = clut_spec[0]
    #     clut_width = clut_spec[1]
    #     clut_height = clut_spec[2]

    #     clutpath = Path(f"output/images/SYSTEM/{clut_name}.0.mode2.PNG")

    #     filepath = Path(f"output/processed/SYSTEM/{filename}")
    #     with open(filepath, "rb") as f:
    #         data = f.read()

    #         for clut_x in range(clut_width):
    #             for clut_y in range(clut_height):
    #                 clut = load_clut(clutpath, clut_x * 16, clut_y, 0)

    #                 mode = 0
    #                 img, _ = parse_img(data, 256, 256, mode, palette=clut)
    #                 if img:
    #                     outputpath = Path(f"output/images/SYSTEM/{filename}.PNG")
    #                     outputpath = outputpath.with_suffix(f".mode{mode}.clut-{clut_name}-{clut_x}-{clut_y}.PNG")
    #                     img.save(outputpath)
