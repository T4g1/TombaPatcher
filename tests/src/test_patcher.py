import filecmp

from tests import get_path

from game_parser.grpx import grpx_extract, grpx_format, GRPX_SUFFIX
from game_parser.files import save_file, load_file
from game_parser.ld import FileInfo
from game_parser.gam import UNGAM_SUFFIX, GAM_SUFFIX, gam, ungam

from common import to_basepath

PATCHER_PATH = "patcher"

IMG_FILE = "CLUT01.0.1080.mode2.PNG"


def test_patcher(tmp_path):
    """Compress and decompress PNG <-> GAM"""
    base = get_path(PATCHER_PATH)
    img = base / IMG_FILE

    formated = to_basepath(img, tmp_path).with_suffix("").with_suffix("")
    ld_file = to_basepath(formated, tmp_path).with_suffix(UNGAM_SUFFIX)
    gam_file = to_basepath(ld_file, tmp_path).with_suffix(GAM_SUFFIX)

    info = FileInfo(base, ld_address=0, index=0, type=0x1080, ram_address=0, size=0)

    # PNG to formated
    grpx_format(img, formated)
    # Formated to LD
    save_file(formated, ld_file, info, 0)
    # LD to GAM
    gam(ld_file, gam_file)

    rev_ld_file = ld_file.with_suffix(".rev" + UNGAM_SUFFIX)
    rev_formated_file = formated.with_suffix(".rev" + GRPX_SUFFIX)
    rev_img_file = to_basepath(img, tmp_path).with_suffix(".rev.PNG")

    # GAM to LD
    ungam(gam_file, rev_ld_file)
    # LD to formated
    load_file(rev_ld_file, rev_formated_file, info, 0)
    # Fortmated to IMG
    grpx_extract(rev_formated_file, rev_img_file, 256, 32, 2)

    assert filecmp.cmp(formated, rev_formated_file, shallow=False)
    assert filecmp.cmp(ld_file, rev_ld_file, shallow=False)
