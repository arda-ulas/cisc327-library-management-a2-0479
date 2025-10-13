"""
R1 — Add Book to Catalog
Spec highlights (from Requirements Specification):
- Title: required, max 200 chars
- Author: required, max 100 chars
- ISBN: required, EXACTLY 13 DIGITS (not just length), unique
- Total copies: required, positive integer
"""
import pytest

# --- Happy path --------------------------------------------------------------

def test_add_book_valid_inserts_and_defaults(svc, get_book_id):
    ok, msg = svc.add_book_to_catalog(
        "Clean Code", "Robert C. Martin", "9780136083238", 2
    )
    assert ok is True
    # Uniqueness check by re-adding later is covered below.
    assert get_book_id("9780136083238") is not None

# --- Required fields & length limits -----------------------------------------

def test_add_book_rejects_empty_title(svc):
    ok, msg = svc.add_book_to_catalog("", "Author", "9780136083238", 1)
    assert ok is False
    assert "Title" in msg or "required" in msg.lower()

def test_add_book_rejects_title_over_200(svc):
    long_title = "T" * 201
    ok, _ = svc.add_book_to_catalog(long_title, "Author", "9780136083238", 1)
    assert ok is False

def test_add_book_rejects_empty_author(svc):
    ok, msg = svc.add_book_to_catalog("Book", "", "9780136083238", 1)
    assert ok is False
    assert "Author" in msg or "required" in msg.lower()

def test_add_book_rejects_author_over_100(svc):
    long_author = "A" * 101
    ok, _ = svc.add_book_to_catalog("Book", long_author, "9780136083238", 1)
    assert ok is False

# --- ISBN rules ---------------------------------------------------------------

def test_add_book_isbn_must_be_all_digits(svc):
    # contains letters -> should be rejected by spec
    ok, _ = svc.add_book_to_catalog("Book", "Author", "97801360AB238", 1)
    assert ok is False  # spec expectation

def test_add_book_isbn_must_be_unique(svc, get_book_id):
    svc.add_book_to_catalog("B1", "A1", "1234567890123", 1)
    assert get_book_id("1234567890123") is not None
    ok, msg = svc.add_book_to_catalog("B2", "A2", "1234567890123", 1)
    assert ok is False, "duplicate ISBN should be rejected"

# --- Total copies -------------------------------------------------------------

def test_add_book_total_copies_must_be_positive(svc):
    ok, _ = svc.add_book_to_catalog("Book", "Author", "9999999999999", 0)
    assert ok is False
