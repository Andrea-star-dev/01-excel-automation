"""샘플 주문 엑셀 생성기. 실제 데이터 아님, 데모/테스트용 가짜 데이터.

쇼핑몰 3곳에서 받은 주문 엑셀을 가정한다. 컬럼명과 순서, 날짜 형식이
각각 다르게 설계되어 있다 (컬럼 매핑 기능을 테스트하기 위함).
"""
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

RNG = random.Random(42)

PRODUCTS = ["무선 마우스", "기계식 키보드", "USB-C 허브", "노트북 스탠드", "블루투스 스피커"]
BUYERS = ["김가짜", "이테스트", "박샘플", "최데모", "정예시"]

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def _rows(n: int, start_date: datetime):
    for i in range(n):
        yield {
            "order_id": f"ORD-{1000 + i}",
            "date": start_date + timedelta(hours=RNG.randint(0, 20)),
            "product": RNG.choice(PRODUCTS),
            "qty": RNG.randint(1, 3),
            "price": RNG.choice([9900, 15900, 22000, 35000, 48000]),
            "buyer": RNG.choice(BUYERS),
            "status": RNG.choice(["결제완료", "배송중", "배송완료"]),
        }


def build_shop_a(day: datetime) -> pd.DataFrame:
    """쇼핑몰 A: 영문 컬럼명, ISO 날짜."""
    rows = list(_rows(8, day))
    return pd.DataFrame([
        {
            "Order No": r["order_id"],
            "Order Date": r["date"].strftime("%Y-%m-%d %H:%M"),
            "Item Name": r["product"],
            "Qty": r["qty"],
            "Unit Price": r["price"],
            "Customer": r["buyer"],
            "Status": r["status"],
        }
        for r in rows
    ])


def build_shop_b(day: datetime) -> pd.DataFrame:
    """쇼핑몰 B: 한글 컬럼명, 한국식 날짜."""
    rows = list(_rows(6, day))
    return pd.DataFrame([
        {
            "주문번호": r["order_id"],
            "주문일시": r["date"].strftime("%Y.%m.%d %H:%M"),
            "상품명": r["product"],
            "수량": r["qty"],
            "판매단가": r["price"],
            "구매자명": r["buyer"],
            "주문상태": r["status"],
        }
        for r in rows
    ])


def build_shop_c(day: datetime) -> pd.DataFrame:
    """쇼핑몰 C: 약어 컬럼명, 총액 컬럼 포함(합계 검증용)."""
    rows = list(_rows(5, day))
    return pd.DataFrame([
        {
            "ord_no": r["order_id"],
            "ord_dt": r["date"].strftime("%d/%m/%Y %H:%M"),
            "item": r["product"],
            "cnt": r["qty"],
            "price_ea": r["price"],
            "amount": r["qty"] * r["price"],
            "cust_nm": r["buyer"],
            "st": r["status"],
        }
        for r in rows
    ])


def main():
    SAMPLE_DIR.mkdir(exist_ok=True)
    today = datetime(2026, 10, 13)

    build_shop_a(today).to_excel(SAMPLE_DIR / "shop_a_orders.xlsx", index=False)
    build_shop_b(today).to_excel(SAMPLE_DIR / "shop_b_orders.xlsx", index=False)
    build_shop_c(today).to_excel(SAMPLE_DIR / "shop_c_orders.xlsx", index=False)

    print(f"샘플 엑셀 3개 생성 완료: {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
