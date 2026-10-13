from pathlib import Path

import pytest

from excel_automation.mapping import load_mapping

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "column_mapping.yaml"


def test_load_mapping_reads_all_sources():
    config = load_mapping(CONFIG_PATH)
    assert {s.name for s in config.sources} == {"shop_a", "shop_b", "shop_c"}
    assert "order_id" in config.canonical_fields


def test_match_picks_correct_source_by_filename():
    config = load_mapping(CONFIG_PATH)
    assert config.match("shop_a_orders.xlsx").name == "shop_a"
    assert config.match("shop_b_orders.xlsx").name == "shop_b"
    assert config.match("shop_c_orders.xlsx").name == "shop_c"


def test_match_raises_for_unknown_file():
    config = load_mapping(CONFIG_PATH)
    with pytest.raises(ValueError):
        config.match("unknown_shop_orders.xlsx")


def test_shop_a_columns_map_to_canonical_fields():
    config = load_mapping(CONFIG_PATH)
    shop_a = config.match("shop_a_orders.xlsx")
    assert shop_a.columns["Order No"] == "order_id"
    assert shop_a.columns["Unit Price"] == "unit_price"
