# 쇼핑몰 주문 엑셀 자동 정리 도구

[![CI](https://github.com/Junoh-Lee111/01-excel-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/Junoh-Lee111/01-excel-automation/actions/workflows/ci.yml)

여러 쇼핑몰(스마트스토어, 쿠팡, 자사몰 등)에서 내려받은 **컬럼 형식이 서로 다른** 주문 엑셀을
한 번에 합쳐서, 보기 좋게 정리된 엑셀 리포트와 매출 요약 메일을 자동으로 만들어주는 도구입니다.

## 이런 분께 유용합니다

- 매일 여러 쇼핑몰의 주문 엑셀을 하나씩 열어서 수동으로 복사·붙여넣기 하고 있다면
- 쇼핑몰마다 컬럼 이름/순서가 달라서 엑셀 함수로 합치기가 번거롭다면
- 매일 아침 "어제 얼마 팔렸는지" 요약을 받아보고 싶다면

## 무엇을 만들어 주나요

1. **정리된 엑셀 1개** — 모든 쇼핑몰 주문을 합친 원본 내역 + 날짜별 매출 요약 +
   상품별 매출 순위, 이렇게 3개 시트로 구성되어 있고 색/굵기 등 서식이 적용되어 있습니다.
2. **요약 메일(HTML)** — 오늘 매출, 날짜별 요약, 잘 팔린 상품 상위 5개를 보여줍니다.
   메일 서버(SMTP) 정보를 설정하면 실제로 메일이 발송되고, 설정하지 않으면 미리보기
   파일로 저장되어 바로 확인할 수 있습니다.

> 결과 스크린샷 자리
>
> - [ ] 엑셀 리포트 스크린샷 (주문내역 / 일일매출요약 / 상품별매출 시트)
> - [ ] 메일 미리보기 스크린샷

## 사용 방법

### 1. 설치

```bash
python -m venv .venv
source .venv/bin/activate   # Windows는 .venv\Scripts\activate
pip install -e .
```

(`pip install -e .`로 실행에 필요한 라이브러리와 `excel-automation` 명령어가 함께 설치됩니다.)

### 2. 쇼핑몰 주문 엑셀 준비

쇼핑몰별로 받은 주문 엑셀 파일들을 한 폴더(예: `sample_data/`)에 모아둡니다.
각 쇼핑몰의 컬럼명이 다르면, `config/column_mapping.yaml`에 해당 쇼핑몰의
파일명 패턴과 컬럼 매핑을 한 번만 등록해두면 됩니다. (예시가 이미 들어있습니다.)

### 3. 실행

```bash
excel-automation run \
  --input-dir sample_data \
  --mapping config/column_mapping.yaml \
  --output-dir output
```

실행이 끝나면 `output/` 폴더에 날짜가 붙은 엑셀 리포트와, 메일 미리보기 파일이 생성됩니다.

### 4. 실제 메일 발송하고 싶다면

`config/smtp.yaml.example`을 복사해 `config/smtp.yaml`로 만들고 메일 서버 정보를
채운 뒤, 실행할 때 `--smtp-config config/smtp.yaml` 옵션을 추가하면 자동으로 메일이
발송됩니다. 설정 파일이 없으면 항상 안전하게 미리보기 파일만 만들어집니다.

## 샘플 데이터로 바로 테스트해보기

이 저장소에는 가짜 쇼핑몰 3곳(A, B, C)의 샘플 주문 엑셀이 `sample_data/`에 들어있습니다.
(실제 개인정보나 실제 주문 데이터가 아닙니다.) 위 3번 실행 명령을 그대로 복사해서 바로
결과물을 확인해볼 수 있습니다.

## 개발/테스트

```bash
pip install -r requirements.txt   # pytest 설치
pytest
```
