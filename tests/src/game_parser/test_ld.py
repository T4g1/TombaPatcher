import shutil
from tests import get_path

from game_parser.ld import load_ld, write_ld, FileInfo

LD_DIR = "ld"
LD_FILE = "LDAR18.BIN"


def test_load_ld():
    file = get_path(LD_DIR) / LD_FILE
    files = load_ld(file)

    assert len(files) == 39

    info = files[4]
    assert info.ld_address == 80
    assert info.ram_address == 0
    assert info.size == 7868
    assert info.width == 0
    assert info.height == 0
    assert info.index == 0
    assert info.type == 0x39FF


def test_write_ld(tmp_path):
    file = tmp_path / LD_FILE

    shutil.copy(get_path(LD_DIR) / LD_FILE, file)

    for index in range(30):
        info_changed = FileInfo(
            file,
            index * 20,
            index=13,
            type=0x1080,
            ram_address=0,
            size=1337,
            width=0,
            height=0,
            x=0,
            y=0,
            header=bytes(4),
        )

        write_ld(info_changed)

        results = load_ld(file)

        info_result = results[index]
        assert info_changed.ld_address == info_result.ld_address
        assert info_changed.ram_address == info_result.ram_address
        assert info_changed.size == info_result.size
        assert info_changed.width == info_result.width
        assert info_changed.height == info_result.height
        assert info_changed.index == info_result.index
        assert info_changed.type == info_result.type
