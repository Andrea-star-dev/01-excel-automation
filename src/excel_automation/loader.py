"""매핑 설정에 따라 쇼핑몰별 주문 엑셀을 공통 스키마 DataFrame으로 변환."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from excel_automation.mapping import MappingConfig, SourceMapping

CANONICAL_ORDER = [
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


def load_order_file(path: Path, source: SourceMapping) -> pd.DataFrame:
    df = pd.read_excel(path)
    df = df.rename(columns=source.columns)

    missing = set(source.columns.values()) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: 매핑된 컬럼이 원본에 없습니다: {missing}")

    df["order_date"] = pd.to_datetime(df["order_date"], format=source.date_format)

    if "total_amount" not in df.columns:
        df["total_amount"] = df["quantity"] * df["unit_price"]
    else:
        df["total_amount"] = df["total_amount"].fillna(df["quantity"] * df["unit_price"])

    df["source"] = source.name
    return df[CANONICAL_ORDER]


def load_all_orders(input_dir: Path, mapping: MappingConfig) -> pd.DataFrame:
    """input_dir 안의 모든 .xlsx 파일을 읽어 하나의 DataFrame으로 합친다."""
    files = sorted(Path(input_dir).glob("*.xlsx"))
    if not files:
        raise ValueError(f"{input_dir}에 엑셀 파일이 없습니다.")

    frames = []
    for path in files:
        source = mapping.match(path.name)
        frames.append(load_order_file(path, source))

    combined = pd.concat(frames, ignore_index=True)
    return combined.sort_values("order_date").reset_index(drop=True)
