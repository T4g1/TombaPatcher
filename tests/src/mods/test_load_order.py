from tests import get_path

from patcher.mods import LoadOrder

LOAD_ORDER_PATH = "mods/load_order.json"


def test_load_order():
    file = get_path(LOAD_ORDER_PATH)

    with open(file, "r") as file:
        load_order = LoadOrder.model_validate_json(file.read())

    assert load_order.order == ["player_skin", "sin_city_color", "archipelago"]
    assert load_order.order[1] == "sin_city_color"
