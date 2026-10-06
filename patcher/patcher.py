from pathlib import Path
from pydantic import ValidationError

from pipeline.orchestrator import create_orchestrator, MultiStageOrchestrator

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


class Patcher:
    orchestrator: MultiStageOrchestrator

    def __init__(self):
        self.orchestrator = create_orchestrator()

    def patch(self, game: Path, output: Path):
        self.extract(game)
        self.apply_mods()
        self.compile(output)

    def extract(self, game: Path):
        """Extraction step"""
        dumpsxiso(game, ISO_PATH)
        ungam_all(ISO_PATH, GAM_PATH)
        self._flas = flas_load_with_lbas(ENTRY_PATH, XML_PATH)
        self._infos = ld_load_all(ISO_PATH, LD_PATH, SYS_PATH, self._flas, GAM_PATH)
        unpacked = files_unpack(ISO_PATH, LD_PATH, self._infos, GAM_PATH, self._flas)

        for info, path in unpacked:
            self.orchestrator.add_task(
                path, params={"width": info.width, "height": info.height}
            )

        self.orchestrator.process(forward=True)

    def apply_mods(self):
        """Return list of updated file paths"""
        try:
            updated_path = self._apply_mods(LD_PATH)

            self._updated_tokens = []
            for path in updated_path:
                self._updated_tokens.append(to_matching_token(path))

                task = self.orchestrator.get_task(path)
                task.ready()
        except (FileNotFoundError, ValidationError) as exception:
            logger.info(f"Unable to apply mods: {exception}")

    def compile(self, output: Path = OUTPUT_PATH):
        self.orchestrator.process(forward=False)

        updated_infos = files_pack(LD_PATH, ISO_PATH, self._infos, GAM_PATH, self._flas)
        gam_all(GAM_PATH, ISO_PATH, self._updated_tokens)
        ld_write_all(updated_infos)
        # TODO: Recompute LBA addresses to align on updated file sizes if needed
        flas_update(ISO_PATH, ENTRY_PATH, self._flas)
        mkpsxiso(output)

    def _apply_mods(self, path: Path):
        updated: set[Path] = set()

        mods = ModsManager(MODS_PATH)
        for command in mods.commands():
            updated |= command.apply(path)

        return updated


if __name__ == "__main__":
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"

    patcher = Patcher()
    patcher.patch(game_path, patched_path)
