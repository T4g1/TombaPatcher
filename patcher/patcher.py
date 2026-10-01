from pathlib import Path
from pydantic import ValidationError

from game_parser.files import unpack as files_unpack, pack as files_pack
from game_parser.packed import unpack_all, pack_all_files
from game_parser.rle import decompress_all, compress_all
from game_parser.tim import tim_to_png_all, png_to_tim_all

from patcher.mods import Mods

from common import (
    LD_PATH,
    PACKED_PATH,
    RLE_PATH,
    TIM_PATH,
    MODS_PATH,
)


def apply_mods():
    mods = Mods(MODS_PATH)
    for command in mods.commands():
        print(command)

    raise Exception("KAPOOT")


def patch(game: Path, output: Path):
    files_unpack(game)
    unpacked_files = unpack_all(LD_PATH, PACKED_PATH)
    decompress_all(PACKED_PATH, RLE_PATH)
    tim_to_png_all(RLE_PATH, TIM_PATH)

    try:
        apply_mods()
    except (FileNotFoundError, ValidationError) as exception:
        print(f"Unable to apply mods: {exception}")

    png_to_tim_all(TIM_PATH, RLE_PATH)
    compress_all(RLE_PATH, PACKED_PATH)
    pack_all_files(PACKED_PATH, LD_PATH, unpacked_files)
    files_pack(output)
