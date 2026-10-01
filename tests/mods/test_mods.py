from tests import get_path

from patcher.mods import Mods

MODS_PATH = "mods"


def test_mods_commands():
    mods = Mods(get_path(MODS_PATH))
    commands = [command for command in mods.commands()]

    assert len(commands) == 2

    command = commands[0]
    assert command.file_pattern == "AREA../A00.\\.0\\.60FF\\.0000"
    assert command.address is None

    command = commands[1]
    assert command.file_pattern == "AREA../CLUT.*"
    assert command.address is None
