from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from workshop_common import chunk_records, normalize_row, parse_file


def test_parser_and_chunker_need_no_api_key(tmp_path: Path) -> None:
    source = tmp_path / "guide.txt"
    source.write_text("one two three four five six", encoding="utf-8")

    records = parse_file(str(source))
    chunks = chunk_records(records, size=4, overlap=1)

    assert records[0]["text"].startswith("one two")
    assert len(chunks) == 2
    assert chunks[0]["metadata"]["record"] == 0


def test_normalizer_maps_common_quality_columns() -> None:
    event = normalize_row(
        {"Failure Mode": "Cracked housing", "Severity": "8", "Reference": "QMS-42"},
        supplier_id="supplier-1",
        source_system="QMS",
        filename="issues.csv",
    )

    assert event["title"] == "Cracked housing"
    assert event["severity"] == "high"
    assert event["source_reference"] == "QMS-42"