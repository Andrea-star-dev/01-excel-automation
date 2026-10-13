"""컬럼 매핑 YAML 로드 + 원본 파일명을 매핑 설정에 매칭."""
from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

import yaml


@dataclass(frozen=True)
class SourceMapping:
    name: str
    file_pattern: str
    date_format: str
    columns: dict[str, str]  # 원본 컬럼명 -> 공통 스키마 필드명


@dataclass(frozen=True)
class MappingConfig:
    sources: list[SourceMapping]
    canonical_fields: list[str]

    def match(self, filename: str) -> SourceMapping:
        for source in self.sources:
            if fnmatch(filename, source.file_pattern):
                return source
        raise ValueError(
            f"'{filename}'에 매칭되는 매핑 설정이 없습니다. "
            f"column_mapping.yaml의 file_pattern을 확인하세요."
        )


def load_mapping(path: str | Path) -> MappingConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    sources = [
        SourceMapping(
            name=name,
            file_pattern=spec["file_pattern"],
            date_format=spec["date_format"],
            columns=spec["columns"],
        )
        for name, spec in raw["sources"].items()
    ]
    return MappingConfig(sources=sources, canonical_fields=raw["canonical_fields"])
