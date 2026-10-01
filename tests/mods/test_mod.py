from tests import get_path

from patcher.mods import Mod

MOD_PATH = "mods/mod.json"


def test_mod():
    file = get_path(MOD_PATH)

    with open(file, "r") as file:
        mod = Mod.model_validate_json(file.read())

    assert mod.name == "Player Skin"
    assert mod.description == "Replace the player skin with Open Source quality content"
    assert mod.version == "0.0.1"
    assert len(mod.patchs) == 1

    patch = mod.patchs[0]
    assert patch.file == "player/A005.0.60FF.0000.PNG"
    assert len(patch.targets) == 1

    target = patch.targets[0]
    assert target.pattern == "AREA../A00.\\.0\\.60FF\\.0000"
    assert target.address is None
