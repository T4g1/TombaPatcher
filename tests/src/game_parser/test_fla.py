import shutil
from tests import get_path

from game_parser.fla import (
    flas_load_with_lbas,
    flas_update,
    FLA_ADDRESS,
    FLA_ENTRY_COUNT,
    FLA_ENTRY_SIZE,
)

from common import to_basepath

FLA_DIR = "fla"

ENTRY_FILE = "SCUS_942.36"
TARGET_FILE = "SCUS_942.36.updated"
XML_FILE = "tomba.xml"
DUMMY_FILE = "DUMMY"


def test_fla_write(tmp_path):
    res = get_path(FLA_DIR)
    entry = res / ENTRY_FILE
    target = res / TARGET_FILE
    xml = res / XML_FILE
    test_file = res / DUMMY_FILE

    entry_result = to_basepath(entry, tmp_path)

    shutil.copy(entry, entry_result)
    shutil.copy(test_file, to_basepath(test_file, tmp_path))

    flas = flas_load_with_lbas(entry, xml)
    fla = flas[0]
    fla.path = f"{FLA_DIR}/{DUMMY_FILE}"
    flas = {0: flas[0]}

    flas_update(tmp_path, entry_result, flas)

    with open(entry, "rb") as f:
        input_data = f.read()

    with open(target, "rb") as f:
        target_data = f.read()

    with open(entry_result, "rb") as f:
        result_data = f.read()

    fla_size = FLA_ENTRY_COUNT * FLA_ENTRY_SIZE

    input = input_data[FLA_ADDRESS : FLA_ADDRESS + fla_size]
    target = target_data[FLA_ADDRESS : FLA_ADDRESS + fla_size]
    result = result_data[FLA_ADDRESS : FLA_ADDRESS + fla_size]

    assert input != result
    assert target == result
