from pathlib import Path
from pydantic import BaseModel
from collections.abc import Iterator

from patcher.patch import Patch, PatchCommand

MOD_ENTRY_NAME = "mod.json"
LOAD_ORDER_NAME = "load_order.json"


class Mod(BaseModel):
    name: str
    version: str
    description: str
    patchs: list[Patch]

    base: Path | None = None

    @classmethod
    def get_path(cls, base: Path, name: str) -> Path:
        return base / name / MOD_ENTRY_NAME

    def set_base(self, base: Path):
        self.base = base

    def commands(self) -> Iterator[PatchCommand]:
        if self.base is None:
            return

        for patch in self.patchs:
            yield from patch.commands(self.base)


class LoadOrder(BaseModel):
    order: list[str]

    def load_mods(self, base: Path) -> Iterator[Mod]:
        for name in self.order:
            with open(Mod.get_path(base, name), "r") as f:
                mod = Mod.model_validate_json(f.read())
                mod.set_base(base / name)
                yield mod


class Mods:
    base: Path
    mods: list[Mod]

    def __init__(self, base: Path):
        self.mods = []

        self.discover(base)

    def discover(self, base: Path):
        self.base = base

        with open(base / LOAD_ORDER_NAME, "r") as f:
            self.load_order = LoadOrder.model_validate_json(f.read())

    def commands(self) -> Iterator[PatchCommand]:
        for mod in self.load_order.load_mods(self.base):
            yield from mod.commands()
