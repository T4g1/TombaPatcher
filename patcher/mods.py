from pathlib import Path
from pydantic import BaseModel, PrivateAttr
from collections.abc import Iterator

from patcher.patch import Patch, PatchCommand

from common import (
    MODS_PATH,
)

MOD_ENTRY_NAME = "mod.json"
LOAD_ORDER_NAME = "load_order.json"


class Mod(BaseModel):
    name: str
    version: str
    description: str
    patchs: list[Patch]

    base: Path | None = None

    _is_valid: bool = PrivateAttr(default=False)
    _is_active: bool = PrivateAttr(default=False)
    _code: str = PrivateAttr(default="")
    _error: str = PrivateAttr(default="")

    @classmethod
    def create_empty(cls, code: str, error: str):
        self = cls(name=code, description="", version="", patchs=[])

        self._is_valid = False
        self._error = error

        return self

    @classmethod
    def get_path(cls, base: Path, name: str) -> Path:
        return base / name / MOD_ENTRY_NAME

    def set_base(self, base: Path, code: str):
        self.base = base / code
        self._code = code

    def commands(self) -> Iterator[PatchCommand]:
        if self.base is None:
            return

        for patch in self.patchs:
            yield from patch.commands(self.base)


class LoadOrder(BaseModel):
    order: list[str]


class ModsManager:
    base: Path
    mods: list[Mod]

    def __init__(self, base: Path):
        self.refresh(base)

    def refresh(self, base: Path):
        self.mods = []
        self.base = base

        # Loads mod load order
        with open(base / LOAD_ORDER_NAME, "r") as f:
            load_order = LoadOrder.model_validate_json(f.read())

        for code in load_order.order:
            mod = self.load_mod(self.base, code)
            mod._is_active = True
            self.mods.append(mod)

        # Loads mod directories
        codes = [path.name for path in MODS_PATH.iterdir()]
        for code in codes:
            if self.is_loaded(code):
                continue

            mod = self.load_mod(self.base, code)
            self.mods.append(mod)

    def is_loaded(self, code: str) -> bool:
        """Indicate if that mod is already loaded"""
        for mod in self.mods:
            if mod._code == code:
                return True
        return False

    def load_mod(self, base: Path, code: str) -> Mod:
        try:
            with open(Mod.get_path(base, code), "r") as f:
                mod = Mod.model_validate_json(f.read())
        except Exception as exception:
            mod = Mod.create_empty(code, str(exception))

        mod.set_base(base, code)
        return mod

    def commands(self) -> Iterator[PatchCommand]:
        """Yield all commands to apply from the activated mods
        in the given order"""
        for mod in self.mods:
            if mod._is_active:
                yield from mod.commands()
