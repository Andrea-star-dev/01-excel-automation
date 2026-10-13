from pathlib import Path

from click.testing import CliRunner

from excel_automation.cli import main

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "column_mapping.yaml"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def test_run_command_generates_report_and_preview(tmp_path):
    runner = CliRunner()
    output_dir = tmp_path / "output"

    result = runner.invoke(
        main,
        [
            "run",
            "--input-dir", str(SAMPLE_DIR),
            "--mapping", str(CONFIG_PATH),
            "--output-dir", str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "미리보기 파일 생성" in result.output
    assert (output_dir / "email_preview.html").exists()
    assert any(output_dir.glob("daily_report_*.xlsx"))
