import filecmp

from tests import get_path

from common import all, to_basepath, PNG_SUFFIX

from game_parser.tim import TIM_SUFFIX, tim_to_png, png_to_tim

TIM_DIR = "tim"


def test_tim_to_png(tmp_path):
    dir = get_path(TIM_DIR)
    for source in dir.rglob(all(TIM_SUFFIX)):
        output = to_basepath(source, tmp_path).with_suffix(PNG_SUFFIX)

        tim_to_png(source, output)

        assert filecmp.cmp(source.with_suffix(PNG_SUFFIX), output, shallow=False)


def test_png_to_tim(tmp_path):
    dir = get_path(TIM_DIR)
    for source in dir.rglob(all(PNG_SUFFIX)):
        output = to_basepath(source, tmp_path).with_suffix(TIM_SUFFIX)

        png_to_tim(source, output)

        assert filecmp.cmp(source.with_suffix(TIM_SUFFIX), output, shallow=False)
