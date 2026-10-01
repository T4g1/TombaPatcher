from pathlib import Path
import filecmp

from tests import get_path

from game_parser.packed import unpack, pack

PACKED_RLE_FILE = "packed/A005.0.60FF.RLE.PAK"
PACKED_5080_FILE = "packed/D103.0.5080.PAK"


def test_unpack_rle(tmp_path: Path):
    path = get_path(PACKED_RLE_FILE)

    unpacked = unpack(path, tmp_path)

    assert len(unpacked) == 0x0166

    for i in range(len(unpacked)):
        file = unpacked[i]
        assert file.suffix == ".RLE"
        assert Path(file.stem).suffix == f".{i:04X}"


def test_unpack_5080(tmp_path: Path):
    path = get_path(PACKED_5080_FILE)

    unpacked = unpack(path, tmp_path)

    assert len(unpacked) == 0x003C

    for i in range(len(unpacked)):
        file = unpacked[i]
        assert file.suffix == ".5080"
        assert Path(file.stem).suffix == f".{i:04X}"


def test_pack_rle(tmp_path: Path):
    path = get_path(PACKED_RLE_FILE)
    result = tmp_path / path.name

    unpack(path, tmp_path)
    pack(tmp_path / "packed", result)

    # Some of the RLE files have the last offset close to the end with
    # 0 to 3 bytes offset
    assert not filecmp.cmp(path, result, shallow=False)

    fixed = path.with_suffix(path.suffix + ".fixed")
    assert filecmp.cmp(
        fixed, result, shallow=False
    ), "Packed and re-packed file differs"


def test_pack_5080(tmp_path: Path):
    path = get_path(PACKED_5080_FILE)
    result = tmp_path / path.name

    unpack(path, tmp_path)
    pack(tmp_path / "packed", result)

    assert filecmp.cmp(path, result, shallow=False), "Packed and re-packed file differs"
