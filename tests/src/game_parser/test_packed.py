from pathlib import Path
import filecmp
import struct

from tests import get_path

from game_parser.packed import unpack, pack, pack_all_files

PACKED_DIR = "packed"
TEST_MULTIPLE_DIR = "packed/test_multiple_files"

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


def test_pack_multiple(tmp_path: Path):
    base = get_path(TEST_MULTIPLE_DIR)
    result = tmp_path / "SUB1/D1234.5080.PAK"

    pack_all_files(base, tmp_path, {tmp_path / "SUB1/D1234.5080.PAK"})

    with open(result, "rb") as f:
        count = struct.unpack("<I", f.read(4))[0]

    assert count == 2
