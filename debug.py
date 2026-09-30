from pathlib import Path

from game_parser.tim import TIM_SUFFIX, png_to_tim
from game_parser.rle import RLE_SUFFIX, compress
from game_parser.packed import PACKED_SUFFIX, pack
from game_parser.files import pack as files_pack

from common import all, to_basepath, TIM_PATH, RLE_PATH, PACKED_PATH, LD_PATH

if __name__ == "__main__":
    # TIM: PNG to TIM
    for file in TIM_PATH.rglob(all(".PNG")):
        png_to_tim(file, to_basepath(file, RLE_PATH).with_suffix(TIM_SUFFIX))

    # RLE: Re-compress
    for file in RLE_PATH.rglob(all(TIM_SUFFIX)):
        compress(file, to_basepath(file, PACKED_PATH).with_suffix(RLE_SUFFIX))

    # Packed: Re-pack files
    file_list = [file for file in PACKED_PATH.rglob(all(RLE_SUFFIX))]
    pak_files = set()
    for file_path in file_list:
        parts = file_path.name.split(".")
        cleaned_parts = parts[:-2] + [parts[-1]]

        new_name = ".".join(cleaned_parts) + PACKED_SUFFIX
        pak_files.add(file_path.parent / new_name)

    for pak_file in pak_files:
        pack(PACKED_PATH, to_basepath(pak_file, LD_PATH))

    # LD
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"
    files_pack(patched_path)
