import pytest
import shutil
import filecmp
from pathlib import Path

from tests import get_path

from pipeline.orchestrator import create_orchestrator

ORCHESTRATOR_PATH = "orchestrator"

FORWARD_PATH = "forward"
REVERSE_PATH = "reverse"

TEST_RLE_PARSER_FILE = "rle/A005-1-002E.62FF.TIM.RLE"
TEST_GAM_PARSER_FILE = "gam/CLUT01.GAM"
TEST_PAK_PARSER_FILE = "pak/A005-0.PAK"
TEST_TIM_PARSER_FILE = "tim/A005-1-002E.62FF.TIM"
TEST_GRPX_PARSER_FILE = "grpx/A001.0.10FF.GRPX"

TESTING_FILES = [
    (TEST_RLE_PARSER_FILE, {}),
    (TEST_GAM_PARSER_FILE, {}),
    (TEST_PAK_PARSER_FILE, {}),
    (TEST_TIM_PARSER_FILE, {}),
    (TEST_GRPX_PARSER_FILE, {"width": 128, "height": 256}),
]


def assert_results(input_dir: Path, output_dir: Path):
    for input in input_dir.glob("*.*"):
        output = output_dir / input.name
        assert filecmp.cmp(input, output, shallow=False), f"{input} != {output}"


@pytest.mark.parametrize("file, params", TESTING_FILES)
def test_orchestrator_files(tmp_path, file: str, params: dict[str, int]):
    path = get_path(ORCHESTRATOR_PATH) / file
    parser_dir = path.parent.name
    base = get_path(ORCHESTRATOR_PATH) / parser_dir

    base_tmp = tmp_path / parser_dir
    base_tmp.mkdir(parents=True, exist_ok=True)

    orchestrator = create_orchestrator()

    target = base_tmp / path.name
    shutil.copy(path, target)
    orchestrator.add_task(target, params=params)

    orchestrator.process(forward=True)
    assert_results(base / FORWARD_PATH, base_tmp)

    orchestrator.ready_all()

    orchestrator.process(forward=False)
    assert_results(base / REVERSE_PATH, base_tmp)
