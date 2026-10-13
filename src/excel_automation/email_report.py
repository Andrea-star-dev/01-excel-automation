"""일일 매출 요약을 HTML로 만들고, SMTP 설정이 있으면 메일 발송,
없으면 미리보기 HTML 파일로 저장한다.
"""
from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd
import yaml

from excel_automation.aggregate import daily_product_summary, daily_summary


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    to_addrs: list[str]
    use_tls: bool = True


def load_smtp_config(path: str | Path | None) -> SmtpConfig | None:
    """SMTP 설정 파일이 없거나 비어있으면 None (= 미리보기 모드로 동작)."""
    if path is None:
        return None
    path = Path(path)
    if not path.exists():
        return None

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    required = {"host", "port", "username", "password", "from_addr", "to_addrs"}
    if not required.issubset(raw):
        return None

    return SmtpConfig(
        host=raw["host"],
        port=int(raw["port"]),
        username=raw["username"],
        password=raw["password"],
        from_addr=raw["from_addr"],
        to_addrs=list(raw["to_addrs"]),
        use_tls=bool(raw.get("use_tls", True)),
    )


def build_html_summary(orders: pd.DataFrame) -> str:
    summary = daily_summary(orders)
    product_summary = daily_product_summary(orders)

    total_revenue = int(summary["revenue_total"].sum())
    total_orders = int(summary["order_count"].sum())

    top_products = (
        product_summary.groupby("product")["revenue_total"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    rows = "".join(
        f"<tr><td>{date}</td><td>{count}건</td><td>{qty}개</td>"
        f"<td>{revenue:,.0f}원</td></tr>"
        for date, count, qty, revenue in summary.itertuples(index=False)
    )
    top_rows = "".join(
        f"<tr><td>{product}</td><td>{revenue:,.0f}원</td></tr>"
        for product, revenue in top_products.items()
    )

    return f"""\
<html>
<body style="font-family: sans-serif;">
  <h2>일일 매출 리포트</h2>
  <p>총 주문 {total_orders}건 / 총 매출 <b>{total_revenue:,.0f}원</b></p>

  <h3>날짜별 요약</h3>
  <table border="1" cellpadding="6" cellspacing="0">
    <tr><th>날짜</th><th>주문 수</th><th>판매 수량</th><th>매출</th></tr>
    {rows}
  </table>

  <h3>매출 상위 상품</h3>
  <table border="1" cellpadding="6" cellspacing="0">
    <tr><th>상품</th><th>매출</th></tr>
    {top_rows}
  </table>
</body>
</html>
"""


def send_or_preview(
    html: str,
    output_dir: str | Path,
    smtp_config: SmtpConfig | None,
    subject: str = "일일 매출 리포트",
) -> Path | None:
    """smtp_config가 있으면 메일 발송하고 None 반환.
    없으면 미리보기 html 파일을 저장하고 그 경로를 반환.
    """
    if smtp_config is None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        preview_path = output_dir / "email_preview.html"
        preview_path.write_text(html, encoding="utf-8")
        return preview_path

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = smtp_config.from_addr
    message["To"] = ", ".join(smtp_config.to_addrs)
    message.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(smtp_config.host, smtp_config.port) as server:
        if smtp_config.use_tls:
            server.starttls()
        server.login(smtp_config.username, smtp_config.password)
        server.sendmail(smtp_config.from_addr, smtp_config.to_addrs, message.as_string())

    return None
