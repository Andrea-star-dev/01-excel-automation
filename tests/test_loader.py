from pathlib import Path

from excel_automation.loader import load_all_orders
from excel_automation.mapping import load_mapping

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "column_mapping.yaml"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def test_load_all_orders_merges_every_shop():
    mapping = load_mapping(CONFIG_PATH)
    orders = load_all_orders(SAMPLE_DIR, mapping)

    assert set(orders["source"]) == {"shop_a", "shop_b", "shop_c"}
    assert len(orders) == 8 + 6 + 5  # generate_sample_data.py의 행 수와 일치
    assert list(orders.columns) == [
        "order_id",
        "order_date",
        "product",
        "quantity",
        "unit_price",
        "total_amount",
        "buyer",
        "status",
        "source",
    ]


def test_total_amount_is_quantity_times_unit_price_when_missing():
    mapping = load_mapping(CONFIG_PATH)
    orders = load_all_orders(SAMPLE_DIR, mapping)
    computed = orders["quantity"] * orders["unit_price"]
    assert (orders["total_amount"] == computed).all()


def test_orders_sorted_by_date():
    mapping = load_mapping(CONFIG_PATH)
    orders = load_all_orders(SAMPLE_DIR, mapping)
    assert orders["order_date"].is_monotonic_increasing
