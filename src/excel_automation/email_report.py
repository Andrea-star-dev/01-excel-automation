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

    th_style = (
        "text-align:left;padding:10px 14px;background:#4C56B8;color:#ffffff;"
        "font:600 12px/1.4 'Manrope',Helvetica,Arial,sans-serif;"
        "letter-spacing:0.3px;text-transform:uppercase;"
    )
    td_style = (
        "padding:10px 14px;border-bottom:1px solid #ECE9F4;"
        "font:14px/1.5 'Manrope',Helvetica,Arial,sans-serif;color:#2B2A3A;"
    )

    rows = "".join(
        f'<tr><td style="{td_style}">{date}</td><td style="{td_style}">{count}건</td>'
        f'<td style="{td_style}">{qty}개</td>'
        f'<td style="{td_style}font-weight:600;">{revenue:,.0f}원</td></tr>'
        for date, count, qty, revenue in summary.itertuples(index=False)
    )
    top_rows = "".join(
        f'<tr><td style="{td_style}">{product}</td>'
        f'<td style="{td_style}font-weight:600;">{revenue:,.0f}원</td></tr>'
        for product, revenue in top_products.items()
    )

    # 이메일 클라이언트(특히 Outlook)는 flex/grid/그라디언트를 지원하지 않으므로
    # 표 기반 레이아웃 + 인라인 스타일로 작성한다. 03 챗봇과 같은 인디고/골드
    # 팔레트를 쓰되, 폰트가 차단돼도 무난하도록 안전한 폴백을 둔다.
    return f"""\
<html>
<head>
<meta charset="utf-8">
<style>
  @media (max-width: 600px) {{
    .container {{ width: 100% !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:32px 16px;background:#F3F2F8;">
  <table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0"
         style="margin:0 auto;max-width:600px;background:#ffffff;border:1px solid #E7E4F2;border-radius:16px;overflow:hidden;">
    <tr>
      <td style="height:6px;background:#5B63D6;font-size:0;line-height:0;">&nbsp;</td>
    </tr>
    <tr>
      <td style="padding:36px 36px 24px;">
        <div style="font:italic 500 12px/1.4 Georgia,'Newsreader',serif;letter-spacing:0.5px;color:#8B8FA3;text-transform:uppercase;margin-bottom:6px;">
          Daily Sales Report
        </div>
        <div style="font:700 24px/1.3 'Manrope',Helvetica,Arial,sans-serif;color:#1C1B2E;margin-bottom:16px;">
          일일 매출 리포트
        </div>
        <div style="font:14px/1.6 'Manrope',Helvetica,Arial,sans-serif;color:#55536B;">
          총 주문 <b style="color:#1C1B2E;">{total_orders}건</b> · 총 매출
          <b style="color:#9A7B1E;">{total_revenue:,.0f}원</b>
        </div>
      </td>
    </tr>

    <tr>
      <td style="padding:0 36px 8px;">
        <div style="font:700 11px/1.4 'Manrope',Helvetica,Arial,sans-serif;letter-spacing:0.6px;color:#8B8FA3;text-transform:uppercase;padding-top:12px;border-top:1px solid #ECE9F4;">
          날짜별 요약
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding:8px 28px 20px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
          <tr>
            <th style="{th_style}border-top-left-radius:8px;">날짜</th>
            <th style="{th_style}">주문 수</th>
            <th style="{th_style}">판매 수량</th>
            <th style="{th_style}border-top-right-radius:8px;">매출</th>
          </tr>
          {rows}
        </table>
      </td>
    </tr>

    <tr>
      <td style="padding:0 36px 8px;">
        <div style="font:700 11px/1.4 'Manrope',Helvetica,Arial,sans-serif;letter-spacing:0.6px;color:#8B8FA3;text-transform:uppercase;padding-top:4px;border-top:1px solid #ECE9F4;">
          매출 상위 상품
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding:8px 28px 32px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
          <tr>
            <th style="{th_style}border-top-left-radius:8px;">상품</th>
            <th style="{th_style}border-top-right-radius:8px;">매출</th>
          </tr>
          {top_rows}
        </table>
      </td>
    </tr>

    <tr>
      <td style="padding:16px 36px;background:#FAF8F2;border-top:1px solid #ECE9F4;">
        <span style="font:12px/1.5 'Manrope',Helvetica,Arial,sans-serif;color:#9A9AA8;">
          자동 생성된 리포트입니다.
        </span>
      </td>
    </tr>
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
