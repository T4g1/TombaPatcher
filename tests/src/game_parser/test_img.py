import filecmp

from tests import get_path

from game_parser.image import extract_img, format_img, IMG_SUFFIX

from common import to_basepath, PNG_SUFFIX

IMG_PATH = "img"

IMG_MODE_0_FILE_RAW = "B000.0.1080"
IMG_MODE_2_FILE_RAW = "CLUT01.0.1080"

IMG_MODE_0_FILE_PNG = IMG_MODE_0_FILE_RAW + ".mode0.PNG"
IMG_MODE_2_FILE_PNG = IMG_MODE_2_FILE_RAW + ".mode2.PNG"

IMG_GREYSCALE = "CLUT.PNG"


def test_extract_img(tmp_path):
    res = get_path(IMG_PATH)
    mode_0 = res / IMG_MODE_0_FILE_RAW
    mode_2 = res / IMG_MODE_2_FILE_RAW

    mode_0_check = res / IMG_MODE_0_FILE_PNG
    mode_2_check = res / IMG_MODE_2_FILE_PNG

    mode_0_out = to_basepath(mode_0, tmp_path).with_suffix(PNG_SUFFIX)
    mode_2_out = to_basepath(mode_2, tmp_path).with_suffix(PNG_SUFFIX)

    extract_img(mode_0, mode_0_out, 512, 256, 0)
    extract_img(mode_2, mode_2_out, 256, 32, 2)

    assert filecmp.cmp(mode_0_check, mode_0_out, shallow=False)
    assert filecmp.cmp(mode_2_check, mode_2_out, shallow=False)


def test_format_img(tmp_path):
    res = get_path(IMG_PATH)
    mode_0 = res / IMG_MODE_0_FILE_PNG
    mode_2 = res / IMG_MODE_2_FILE_PNG

    mode_0_check = res / IMG_MODE_0_FILE_RAW
    mode_2_check = res / IMG_MODE_2_FILE_RAW

    mode_0_out = to_basepath(mode_0, tmp_path).with_suffix(IMG_SUFFIX)
    mode_2_out = to_basepath(mode_2, tmp_path).with_suffix(IMG_SUFFIX)

    format_img(mode_0, mode_0_out)
    format_img(mode_2, mode_2_out)

    assert filecmp.cmp(mode_0_check, mode_0_out, shallow=False)
    assert filecmp.cmp(mode_2_check, mode_2_out, shallow=False)


def test_format_img_greyscale(tmp_path):
    res = get_path(IMG_PATH)
    file = res / IMG_GREYSCALE

    file_out = to_basepath(file, tmp_path).with_suffix(IMG_SUFFIX)

    format_img(file, file_out)

    # assert filecmp.cmp(mode_0_check, mode_0_out, shallow=False)
