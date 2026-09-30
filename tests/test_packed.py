from pathlib import Path
import filecmp

from tests import get_path

from game_parser.packed import unpack, pack

PACKED_RLE_FILE = "packed/A005.0.60FF.RLE.PAK"
PACKED_5080_FILE = "packed/D103.0.5080.PAK"


def test_rle_unpack(tmp_path: Path):
    path = get_path(PACKED_RLE_FILE)

    unpacked = unpack(path, tmp_path)

    assert len(unpacked) == 0x0166 + 1

    for i in range(len(unpacked)):
        file = unpacked[i]
        assert file.suffix == ".RLE"
        assert Path(file.stem).suffix == f".{i:04X}"


def test_5080_unpack(tmp_path: Path):
    path = get_path(PACKED_5080_FILE)

    unpacked = unpack(path, tmp_path)

    assert len(unpacked) == 0x003C

    for i in range(len(unpacked)):
        file = unpacked[i]
        assert file.suffix == ".5080"
        assert Path(file.stem).suffix == f".{i:04X}"


def test_rle_pack(tmp_path: Path):
    path = get_path(PACKED_RLE_FILE)
    result = tmp_path / path.name

    unpack(path, tmp_path)
    pack(tmp_path / "packed", result)

    # Theres a bug in the origina PSX compiler: the reported entry count is offseted by -1
    assert not filecmp.cmp(path, result, shallow=False)

    fixed = path.with_suffix(path.suffix + ".fixed")
    assert filecmp.cmp(
        fixed, result, shallow=False
    ), "Packed and re-packed file differs"


def test_5080_pack(tmp_path: Path):
    path = get_path(PACKED_5080_FILE)
    result = tmp_path / path.name

    unpack(path, tmp_path)
    pack(tmp_path / "packed", result)

    assert filecmp.cmp(path, result, shallow=False), "Packed and re-packed file differs"
