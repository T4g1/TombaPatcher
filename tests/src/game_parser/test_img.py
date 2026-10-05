import filecmp

from tests import get_path

from game_parser.grpx import grpx_format, grpx_extract, GRPX_SUFFIX

from common import to_basepath, PNG_SUFFIX

GRPX_PATH = "grpx"

GRPX_MODE_0_FILE_RAW = "test_extract_mode_0.GRPX"
GRPX_MODE_0_FILE_PNG = "test_extract_mode_0.PNG"

GRPX_MODE_2_FILE_RAW = "test_extract_mode_2.GRPX"
GRPX_MODE_2_FILE_PNG = "test_extract_mode_2.PNG"

GRPX_GRAYSCALE_PNG = "test_format_mode_2.PNG"
GRPX_GRAYSCALE_RAW = "test_format_mode_2.GRPX"


def test_grpx_extract(tmp_path):
    res = get_path(GRPX_PATH)
    mode_0_input = res / GRPX_MODE_0_FILE_RAW
    mode_2_input = res / GRPX_MODE_2_FILE_RAW

    mode_0_target = res / GRPX_MODE_0_FILE_PNG
    mode_2_target = res / GRPX_MODE_2_FILE_PNG

    mode_0_output = tmp_path / mode_0_target.with_suffix(PNG_SUFFIX).name
    mode_2_output = tmp_path / mode_2_target.with_suffix(PNG_SUFFIX).name

    grpx_extract(mode_0_input, mode_0_output, 512, 256, 0)
    grpx_extract(mode_2_input, mode_2_output, 256, 32, 2)

    assert filecmp.cmp(mode_0_target, mode_0_output, shallow=False)
    assert filecmp.cmp(mode_2_target, mode_2_output, shallow=False)


def test_grpx_format(tmp_path):
    res = get_path(GRPX_PATH)
    mode_0_input = res / GRPX_MODE_0_FILE_PNG
    mode_2_input = res / GRPX_MODE_2_FILE_PNG

    mode_0_target = res / GRPX_MODE_0_FILE_RAW
    mode_2_target = res / GRPX_MODE_2_FILE_RAW

    mode_0_output = tmp_path / mode_0_target.with_suffix(GRPX_SUFFIX).name
    mode_2_output = tmp_path / mode_2_target.with_suffix(GRPX_SUFFIX).name

    grpx_format(mode_0_input, mode_0_output)
    grpx_format(mode_2_input, mode_2_output)

    assert filecmp.cmp(mode_0_target, mode_0_output, shallow=False)
    assert filecmp.cmp(mode_2_target, mode_2_output, shallow=False)


def test_format_GRPX_grayscale(tmp_path):
    res = get_path(GRPX_PATH)
    file_input = res / GRPX_GRAYSCALE_PNG
    file_target = res / GRPX_GRAYSCALE_RAW

    file_output = to_basepath(file_input, tmp_path).with_suffix(GRPX_SUFFIX)

    grpx_format(file_input, file_output)

    assert filecmp.cmp(file_target, file_output, shallow=False)
