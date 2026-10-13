"""CLI 진입점.

사용 예:
    python -m excel_automation.cli run \\
        --input-dir sample_data \\
        --mapping config/column_mapping.yaml \\
        --output-dir output
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from excel_automation.email_report import build_html_summary, load_smtp_config, send_or_preview
from excel_automation.loader import load_all_orders
from excel_automation.mapping import load_mapping
from excel_automation.report import build_report


@click.group()
def main() -> None:
    """쇼핑몰 주문 엑셀 병합 + 일일 매출 리포트 도구."""


@main.command()
@click.option("--input-dir", required=True, type=click.Path(exists=True, file_okay=False), help="원본 주문 엑셀 폴더")
@click.option("--mapping", required=True, type=click.Path(exists=True, dir_okay=False), help="컬럼 매핑 YAML 경로")
@click.option("--output-dir", required=True, type=click.Path(file_okay=False), help="리포트 출력 폴더")
@click.option("--smtp-config", default=None, type=click.Path(dir_okay=False), help="SMTP 설정 YAML (없으면 미리보기 파일만 생성)")
def run(input_dir: str, mapping: str, output_dir: str, smtp_config: str | None) -> None:
    """주문 엑셀을 합치고, 서식 있는 리포트와 요약 메일(또는 미리보기)을 만든다."""
    mapping_config = load_mapping(mapping)
    orders = load_all_orders(Path(input_dir), mapping_config)

    today = date.today().isoformat()
    report_path = build_report(orders, Path(output_dir) / f"daily_report_{today}.xlsx")
    click.echo(f"리포트 생성: {report_path}")

    html = build_html_summary(orders)
    smtp = load_smtp_config(smtp_config)
    result = send_or_preview(html, output_dir, smtp)

    if result is None:
        click.echo("SMTP 설정 확인됨 — 요약 메일을 발송했습니다.")
    else:
        click.echo(f"SMTP 설정 없음 — 미리보기 파일 생성: {result}")


if __name__ == "__main__":
    main()
