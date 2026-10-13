from pathlib import Path

from excel_automation.aggregate import daily_product_summary, daily_summary
from excel_automation.loader import load_all_orders
from excel_automation.mapping import load_mapping

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "column_mapping.yaml"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def _orders():
    mapping = load_mapping(CONFIG_PATH)
    return load_all_orders(SAMPLE_DIR, mapping)


def test_daily_summary_revenue_matches_raw_total():
    orders = _orders()
    summary = daily_summary(orders)
    assert summary["revenue_total"].sum() == orders["total_amount"].sum()
    assert summary["order_count"].sum() == len(orders)


def test_daily_product_summary_revenue_matches_raw_total():
    orders = _orders()
    product_summary = daily_product_summary(orders)
    assert product_summary["revenue_total"].sum() == orders["total_amount"].sum()
