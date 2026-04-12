# tests/test_dataset.py
import csv
import os
import re
import pytest

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
REQUIRED_COLUMNS = {
    "domain", "probe_question", "wrong_fact", "true_fact",
    "correction_msg", "reassertion_msg", "authority_msg", "expected_answer",
    "ctrl_wrong_user_msg", "ctrl_correct_authority_msg",
}
EXPECTED_DOMAINS = {
    "geography", "science", "history", "nature", "space",
    "medicine", "technology", "sports", "economics", "climate",
}
EXPECTED_TOTAL = 150
EXPECTED_PER_DOMAIN = 15


def load_dataset():
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_dataset_exists():
    assert os.path.exists(DATASET_PATH), f"Dataset not found at {DATASET_PATH}"


def test_dataset_has_correct_columns():
    rows = load_dataset()
    assert rows, "Dataset is empty"
    actual = set(rows[0].keys())
    assert actual == REQUIRED_COLUMNS, (
        f"Column mismatch. Missing: {REQUIRED_COLUMNS - actual}, Extra: {actual - REQUIRED_COLUMNS}"
    )


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


def test_expected_answer_matches_true_fact():
    """Each expected_answer regex must match the corresponding true_fact."""
    rows = load_dataset()
    for i, row in enumerate(rows):
        pattern = row["expected_answer"]
        true_fact = row["true_fact"]
        assert re.search(pattern, true_fact), (
            f"Row {i+1}: expected_answer pattern does not match true_fact. "
            f"pattern={pattern!r}, true_fact={true_fact!r}"
        )


def test_correction_msg_contains_true_fact():
    """correction_msg must contain the verbatim true_fact value."""
    rows = load_dataset()
    for i, row in enumerate(rows):
        assert row["true_fact"] in row["correction_msg"], (
            f"Row {i+1}: correction_msg does not contain true_fact verbatim. "
            f"true_fact={row['true_fact']!r}, correction_msg={row['correction_msg']!r}"
        )


def test_ctrl_wrong_user_msg_contains_wrong_fact():
    """ctrl_wrong_user_msg must contain the verbatim wrong_fact value."""
    rows = load_dataset()
    for i, row in enumerate(rows):
        assert row["wrong_fact"] in row["ctrl_wrong_user_msg"], (
            f"Row {i+1}: ctrl_wrong_user_msg does not contain wrong_fact verbatim. "
            f"wrong_fact={row['wrong_fact']!r}, ctrl_wrong_user_msg={row['ctrl_wrong_user_msg']!r}"
        )


def test_ctrl_correct_authority_msg_contains_true_fact():
    """ctrl_correct_authority_msg must contain the verbatim true_fact value."""
    rows = load_dataset()
    for i, row in enumerate(rows):
        assert row["true_fact"] in row["ctrl_correct_authority_msg"], (
            f"Row {i+1}: ctrl_correct_authority_msg does not contain true_fact verbatim. "
            f"true_fact={row['true_fact']!r}, ctrl_correct_authority_msg={row['ctrl_correct_authority_msg']!r}"
        )
