import filecmp

from tests import get_path

from common import all, to_basepath

from game_parser.rle import RLE_SUFFIX, rle_decompress, rle_compress
from game_parser.tim import TIM_SUFFIX

RLE_DIR = "rle"


def test_rle_decompress(tmp_path):
    rle_dir = get_path(RLE_DIR)
    for source in rle_dir.rglob(all(RLE_SUFFIX)):
        output = to_basepath(source, tmp_path).with_suffix(TIM_SUFFIX)

        rle_decompress(source, output)

        assert filecmp.cmp(source.with_suffix(TIM_SUFFIX), output, shallow=False)


def test_rle_compress(tmp_path):
    rle_dir = get_path(RLE_DIR)
    for source in rle_dir.rglob(all(TIM_SUFFIX)):
        output = to_basepath(source, tmp_path).with_suffix(RLE_SUFFIX)

        rle_compress(source, output)
        rle_decompress(output, output.with_suffix(".check"))

        assert filecmp.cmp(source, output.with_suffix(".check"), shallow=False)
