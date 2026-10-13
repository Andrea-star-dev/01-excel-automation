from pathlib import Path

from excel_automation.email_report import build_html_summary, load_smtp_config, send_or_preview
from excel_automation.loader import load_all_orders
from excel_automation.mapping import load_mapping

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "column_mapping.yaml"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def _orders():
    mapping = load_mapping(CONFIG_PATH)
    return load_all_orders(SAMPLE_DIR, mapping)


def test_build_html_summary_contains_total_revenue():
    orders = _orders()
    html = build_html_summary(orders)
    total_revenue = int(orders["total_amount"].sum())
    assert f"{total_revenue:,.0f}원" in html
    assert "일일 매출 리포트" in html


def test_load_smtp_config_returns_none_when_file_missing(tmp_path):
    assert load_smtp_config(tmp_path / "does_not_exist.yaml") is None


def test_load_smtp_config_returns_none_when_incomplete(tmp_path):
    path = tmp_path / "smtp.yaml"
    path.write_text("host: smtp.example.com\n", encoding="utf-8")
    assert load_smtp_config(path) is None


def test_load_smtp_config_parses_complete_file(tmp_path):
    path = tmp_path / "smtp.yaml"
    path.write_text(
        """
host: smtp.example.com
port: 587
username: user@example.com
password: secret
from_addr: user@example.com
to_addrs:
  - owner@example.com
""",
        encoding="utf-8",
    )
    config = load_smtp_config(path)
    assert config is not None
    assert config.host == "smtp.example.com"
    assert config.to_addrs == ["owner@example.com"]


def test_send_or_preview_writes_preview_file_without_smtp_config(tmp_path):
    orders = _orders()
    html = build_html_summary(orders)
    result = send_or_preview(html, tmp_path, smtp_config=None)

    assert result == tmp_path / "email_preview.html"
    assert result.read_text(encoding="utf-8") == html
