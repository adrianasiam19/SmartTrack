"""Tests for KNUST mapping used by ML alternate recommendations."""

from ml_aspect.knust_mapping import (
    knust_targets_for_ml_class,
    load_knust_programme_index,
    all_mapped_ml_classes,
)


def test_knust_index_loads_catalogue():
    index = load_knust_programme_index()
    assert "MBChB Medicine" in index
    assert "BSc Computer Science" in index
    assert index["BSc Nursing"]["family"] == "Health Sciences"


def test_ml_classes_map_only_to_knust_catalogue():
    index = load_knust_programme_index()
    for ml_class in all_mapped_ml_classes():
        targets = knust_targets_for_ml_class(ml_class)
        assert targets, f"{ml_class} should map to at least one KNUST programme"
        for row in targets:
            assert row["programme"] in index
            assert row["family"] in {"Health Sciences", "Engineering", "Science"}


def test_unmapped_business_class_returns_empty():
    assert knust_targets_for_ml_class("accounting") == []
    assert knust_targets_for_ml_class("law") == []
