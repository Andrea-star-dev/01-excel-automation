"""병합된 주문 데이터로 일일 매출 집계를 만든다."""
from __future__ import annotations

import pandas as pd


def daily_summary(orders: pd.DataFrame) -> pd.DataFrame:
    """날짜별 주문 수 / 판매 수량 / 매출 합계."""
    df = orders.copy()
    df["date"] = df["order_date"].dt.date

    summary = (
        df.groupby("date")
        .agg(
            order_count=("order_id", "count"),
            quantity_total=("quantity", "sum"),
            revenue_total=("total_amount", "sum"),
        )
        .reset_index()
        .sort_values("date")
    )
    return summary


def daily_product_summary(orders: pd.DataFrame) -> pd.DataFrame:
    """날짜 x 상품별 판매 수량 / 매출 합계 (어떤 상품이 잘 팔렸는지)."""
    df = orders.copy()
    df["date"] = df["order_date"].dt.date

    summary = (
        df.groupby(["date", "product"])
        .agg(
            quantity_total=("quantity", "sum"),
            revenue_total=("total_amount", "sum"),
        )
        .reset_index()
        .sort_values(["date", "revenue_total"], ascending=[True, False])
    )
    return summary
