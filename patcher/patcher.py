from pathlib import Path
from pydantic import ValidationError

from game_parser.mkpsxiso import dumpsxiso, mkpsxiso
from game_parser.fla import load_flas_with_lbas
from game_parser.files import unpack as files_unpack, pack as files_pack
from game_parser.gam import ungam_all, gam_all
from game_parser.packed import unpack_all, pack_all_files
from game_parser.rle import decompress_all, compress_all
from game_parser.tim import tim_to_png_all, png_to_tim_all

from patcher.mods import Mods

from common import (
    OUTPUT_PATH,
    ENTRY_PATH,
    XML_PATH,
    SYS_PATH,
    LD_PATH,
    PACKED_PATH,
    RLE_PATH,
    TIM_PATH,
    MODS_PATH,
    GAM_PATH,
    ISO_PATH,
)


def apply_mods():
    """Return list of updated file paths"""
    updated: set[Path] = set()

    mods = Mods(MODS_PATH)
    for command in mods.commands():
        updated |= command.apply(OUTPUT_PATH)

    return updated


def patch(game: Path, output: Path):
    dumpsxiso(game, ISO_PATH)
    ungam_all(ISO_PATH, GAM_PATH)
    flas = load_flas_with_lbas(ENTRY_PATH, XML_PATH)
    files_unpack(ISO_PATH, LD_PATH, SYS_PATH, GAM_PATH, flas)
    unpacked_files = unpack_all(LD_PATH, PACKED_PATH)
    decompress_all(PACKED_PATH, RLE_PATH)
    tim_to_png_all(RLE_PATH, TIM_PATH)

    try:
        updated_path = apply_mods()
        updated = [path.name.split(".")[0] for path in updated_path]
    except (FileNotFoundError, ValidationError) as exception:
        print(f"Unable to apply mods: {exception}")

    png_to_tim_all(TIM_PATH, RLE_PATH)
    compress_all(RLE_PATH, PACKED_PATH)
    pack_all_files(PACKED_PATH, LD_PATH, unpacked_files)
    files_pack(LD_PATH, ISO_PATH, SYS_PATH, GAM_PATH, flas)
    gam_all(GAM_PATH, ISO_PATH, updated)
    mkpsxiso(output)


if __name__ == "__main__":
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"

    patch(game_path, patched_path)
