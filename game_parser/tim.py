import struct
from pathlib import Path

from game_parser.image import parse_img
from game_parser.vram import get_from_16bit_color, COLOR_SIZE

MAGIC_TIM = b"\x10\x00\x00\x00"


def parse_tim_file(data):
    """
    Parses a single TIM image from a binary data buffer at a given offset.
    Returns (Image object, total_bytes_consumed) or (None, 0) if invalid.
    """
    try:
        tag, version, _, flags = struct.unpack_from("<BBHI", data)
        if tag != 0x10 or version != 0:
            return None, 0

        bpp_mode = flags & 0x03  # Bits 0-1: Bit depth mode
        clut_present = (flags >> 3) & 1  # Bit 3: CLUT presence flag

        current_ptr = 8
        palettes = []

        if clut_present:
            clut_length, clut_x, clut_y, clut_w, clut_h = struct.unpack_from(
                "<IHHHH", data, current_ptr
            )

            if clut_w > 200 or clut_h > 200:
                return None, 0

            if clut_w == 0 or clut_h == 0:
                return None, 0

            # The header includes the length word itself, so data size is length - 12
            clut_data_offset = current_ptr + 12

            for i in range(clut_w * clut_h):
                index = clut_data_offset + (i * COLOR_SIZE)
                raw_value = data[index : index + COLOR_SIZE]
                value = int.from_bytes(raw_value, byteorder="little")
                color = get_from_16bit_color(value)

                if color[3] == 0:
                    palettes.append((0, 255, 0))
                else:
                    palettes.append((color[0], color[1], color[2]))

            current_ptr += clut_length

        img_length, img_x, img_y, img_fb_w, img_fb_h = struct.unpack_from(
            "<IHHHH", data, current_ptr
        )
        offset = current_ptr + 12

        img, _ = parse_img(
            data, img_fb_w, img_fb_h, bpp_mode, offset=offset, palette=palettes
        )

        # Total size consumed by this complete TIM file structure
        total_tim_bytes = offset + img_length - 12
        return img, total_tim_bytes

    except Exception:
        return None, 0


def extract_tim(filepath: Path, outputpath: Path, address: int):
    """Extract TIM file
    Return bytes consumed"""

    with open(filepath, "rb") as f:
        data = f.read()

    img, bytes_consumed = parse_tim_file(data[address:])
    if img and img.width > 0 and img.height > 0 and bytes_consumed > 0:
        imgdirectory = outputpath / filepath.parent.name
        imgdirectory.mkdir(parents=True, exist_ok=True)

        imgpath = imgdirectory / filepath.with_suffix(f".{address:08X}.PNG").name
        img.save(imgpath)
        print(f"Extracted TIM file at offset 0x{address:08X} to {imgpath}")


if __name__ == "__main__":
    needle = MAGIC_TIM
    file_pattern = "*.RLE.*.TIM"

    basepath = Path("output/processed")

    for filepath in basepath.rglob(file_pattern):
        with open(filepath, "rb") as file:
            content = file.read()
            address = content.find(needle)

            if address != 0:
                continue

            print(f"Found pattern in: {filepath} at address: 0x{address:X}")
            extract_tim(filepath, Path("output/tim"), address)
