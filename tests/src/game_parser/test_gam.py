from tests import get_path

from common import all

from game_parser.gam import GAM_SUFFIX, gam_all

GAM_DIR = "gam"


def test_gam_all(tmp_path):
    base = get_path(GAM_DIR)
    gam_all(base, tmp_path)

    sources = [file for file in base.rglob(all(GAM_SUFFIX))]
    results = [file for file in tmp_path.rglob(all(GAM_SUFFIX))]

    assert len(sources) == len(results)


def test_gam_all_filtered(tmp_path):
    base = get_path(GAM_DIR)
    sources = [file for file in base.rglob(all(GAM_SUFFIX))]

    gam_all(base, tmp_path, ["AREA00/A001"])

    results = [file for file in tmp_path.rglob(all(GAM_SUFFIX))]

    assert len(sources) == 3
    assert len(results) == 1
