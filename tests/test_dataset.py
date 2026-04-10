# tests/test_dataset.py
import csv
import os
import re
import pytest

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
REQUIRED_COLUMNS = {
    "domain", "probe_question", "wrong_fact", "true_fact",
    "correction_msg", "reassertion_msg", "authority_msg", "expected_answer"
}
EXPECTED_DOMAINS = {"geography", "science", "history", "nature", "space"}
EXPECTED_TOTAL = 75
EXPECTED_PER_DOMAIN = 15


def load_dataset():
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_dataset_exists():
    assert os.path.exists(DATASET_PATH), f"Dataset not found at {DATASET_PATH}"


def test_dataset_has_correct_columns():
    rows = load_dataset()
    assert rows, "Dataset is empty"
    assert set(rows[0].keys()) == REQUIRED_COLUMNS


def test_dataset_row_count():
    rows = load_dataset()
    assert len(rows) == EXPECTED_TOTAL, f"Expected {EXPECTED_TOTAL} rows, got {len(rows)}"


def test_all_domains_present():
    rows = load_dataset()
    domains = {r["domain"] for r in rows}
    assert domains == EXPECTED_DOMAINS, f"Missing domains: {EXPECTED_DOMAINS - domains}"


def test_each_domain_has_15_rows():
    rows = load_dataset()
    for domain in EXPECTED_DOMAINS:
        count = sum(1 for r in rows if r["domain"] == domain)
        assert count == EXPECTED_PER_DOMAIN, f"{domain}: expected 15, got {count}"


def test_no_empty_fields():
    rows = load_dataset()
    for i, row in enumerate(rows):
        for col in REQUIRED_COLUMNS:
            assert row[col].strip(), f"Row {i+1} has empty field: {col}"


def test_expected_answers_are_valid_regex():
    rows = load_dataset()
    for i, row in enumerate(rows):
        try:
            re.compile(row["expected_answer"])
        except re.error as e:
            pytest.fail(f"Row {i+1} has invalid regex in expected_answer: {e}")


def test_correction_msg_contains_true_fact():
    """correction_msg should reference the true fact value."""
    rows = load_dataset()
    for i, row in enumerate(rows):
        true_val_core = row["true_fact"].split()[0].replace(",", "")
        assert true_val_core in row["correction_msg"].replace(",", ""), \
            f"Row {i+1}: correction_msg may not reference true_fact. " \
            f"true_fact={row['true_fact']}, correction_msg={row['correction_msg']}"
