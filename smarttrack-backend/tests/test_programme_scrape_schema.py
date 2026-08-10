"""Schema validation for Course Directory scrape payloads."""
from __future__ import annotations

from scripts.scrape_programmes.common import empty_university_payload, normalize_programme_key, programme_record
from scripts.scrape_programmes.schema import validate_university_payload


def test_normalize_programme_key_strips_degree_prefix() -> None:
    assert normalize_programme_key("BSc Nursing") == "nursing"
    assert normalize_programme_key("Bachelor of Science in Computer Science") == "computer science"


def test_validate_university_payload_ok() -> None:
    payload = empty_university_payload(
        university="University of Ghana",
        university_code="UG",
        source_urls=["https://www.ug.edu.gh/programme-catalogue"],
        status="ok",
        programmes=[
            programme_record(
                name="BSc Nursing",
                university="University of Ghana",
                university_code="UG",
                source_url="https://www.ug.edu.gh/programme-catalogue",
                overview="Train nurses.",
            )
        ],
    )
    assert validate_university_payload(payload) == []


def test_validate_university_payload_reports_missing_name() -> None:
    payload = empty_university_payload(
        university="X",
        university_code="X",
        source_urls=[],
        status="ok",
        programmes=[{"id": "x", "university": "X", "university_code": "X", "source_url": "http://x", "level": "Undergraduate"}],
    )
    errors = validate_university_payload(payload)
    assert any("missing name" in e for e in errors)
