"""
R6 — Search
Spec:
- title/author: partial, case-insensitive
- isbn: exact match
"""
import pytest

def test_search_empty_term_returns_empty(svc):
    assert svc.search_books_in_catalog("", "title") == []
    assert svc.search_books_in_catalog("   ", "author") == []

def test_search_invalid_type_returns_empty(svc):
    assert svc.search_books_in_catalog("anything", "publisher") == []

def test_search_title_partial_case_insensitive(svc, add_and_get_book_id):
    add_and_get_book_id("The Pragmatic Programmer", "Andrew Hunt", "9780201616224", 1)
    add_and_get_book_id("Clean Code", "Robert Martin", "9780132350884", 1)
    results = svc.search_books_in_catalog("pragmatic", "title")
    assert len(results) == 1
    assert results[0]["title"] == "The Pragmatic Programmer"

def test_search_author_partial_case_insensitive(svc, add_and_get_book_id):
    add_and_get_book_id("Book A", "Jane Doe", "1111111111111", 1)
    add_and_get_book_id("Book B", "JANE SMITH", "2222222222222", 1)
    res1 = svc.search_books_in_catalog("jane", "author")
    assert {r["isbn"] for r in res1} == {"1111111111111", "2222222222222"}

def test_search_title_multiple_hits(svc, add_and_get_book_id):
    add_and_get_book_id("Python Tricks", "Dan Bader", "3333333333333", 1)
    add_and_get_book_id("Fluent Python", "Luciano Ramalho", "4444444444444", 1)
    add_and_get_book_id("Effective Java", "Joshua Bloch", "5555555555555", 1)
    res = svc.search_books_in_catalog("python", "title")
    assert {r["isbn"] for r in res} == {"3333333333333", "4444444444444"}

def test_search_isbn_exact_match_only(svc, add_and_get_book_id):
    add_and_get_book_id("Some Book", "Someone", "6666666666666", 1)
    assert svc.search_books_in_catalog("6666666666666", "isbn")[0]["title"] == "Some Book"
    # Should not match partials or wrong ISBN
    assert svc.search_books_in_catalog("666666666666", "isbn") == []
    assert svc.search_books_in_catalog("06666666666666", "isbn") == []
