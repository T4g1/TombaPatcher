from pathlib import Path
from pydantic import ValidationError

from pipeline.orchestrator import create_orchestrator

from game_parser.mkpsxiso import dumpsxiso, mkpsxiso
from game_parser.fla import flas_load_with_lbas, flas_update
from game_parser.ld import ld_load_all, ld_write_all
from game_parser.files import unpack as files_unpack, pack as files_pack
from game_parser.gam import ungam_all, gam_all

from patcher.mods import ModsManager

from common import (
    logger,
    to_matching_token,
    OUTPUT_PATH,
    ENTRY_PATH,
    XML_PATH,
    SYS_PATH,
    LD_PATH,
    MODS_PATH,
    GAM_PATH,
    ISO_PATH,
)


def apply_mods(path: Path = OUTPUT_PATH):
    """Return list of updated file paths"""
    updated: set[Path] = set()

    mods = ModsManager(MODS_PATH)
    for command in mods.commands():
        updated |= command.apply(path)

    return updated


def patch(game: Path, output: Path):
    orchestrator = create_orchestrator()

    dumpsxiso(game, ISO_PATH)
    ungam_all(ISO_PATH, GAM_PATH)
    flas = flas_load_with_lbas(ENTRY_PATH, XML_PATH)
    infos = ld_load_all(ISO_PATH, LD_PATH, SYS_PATH, flas, GAM_PATH)
    unpacked = files_unpack(ISO_PATH, LD_PATH, infos, GAM_PATH, flas)

    for info, path in unpacked:
        orchestrator.add_task(path, params={"width": info.width, "height": info.height})

    orchestrator.process(forward=True)

    try:
        updated_path = apply_mods(LD_PATH)

        updated_tokens = []
        for path in updated_path:
            updated_tokens.append(to_matching_token(path))

            task = orchestrator.get_task(path)
            task.ready()
    except (FileNotFoundError, ValidationError) as exception:
        logger.info(f"Unable to apply mods: {exception}")

    orchestrator.process(forward=False)

    updated_infos = files_pack(LD_PATH, ISO_PATH, infos, GAM_PATH, flas)
    gam_all(GAM_PATH, ISO_PATH, updated_tokens)
    ld_write_all(updated_infos)
    # TODO: Recompute LBA addresses to align on updated file sizes if needed
    flas_update(ISO_PATH, ENTRY_PATH, flas)
    mkpsxiso(output)


if __name__ == "__main__":
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"

    patch(game_path, patched_path)
