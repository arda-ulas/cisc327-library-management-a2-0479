"""
R6 — Search
Expectations:
- Title: partial, case-insensitive
- Author: partial, case-insensitive
- ISBN: exact
"""
import pytest

@pytest.fixture
def catalog_fixture(svc):
    svc.add_book_to_catalog("Clean Code", "Robert Martin", "9780132350884", 1)
    svc.add_book_to_catalog("Clean Architecture", "Robert Martin", "9780134494166", 1)
    svc.add_book_to_catalog("The Pragmatic Programmer", "Andrew Hunt", "9780201616224", 1)

@pytest.mark.xfail(reason="R6 not implemented yet.")
def test_search_by_title_partial_case_insensitive(svc, catalog_fixture):
    ok, books = svc.search_books_in_catalog("clean", "title")
    assert ok is True
    titles = [b["title"].lower() for b in books]
    assert "clean code".lower() in titles and "clean architecture".lower() in titles

@pytest.mark.xfail(reason="R6 not implemented yet.")
def test_search_by_author_partial_case_insensitive(svc, catalog_fixture):
    ok, books = svc.search_books_in_catalog("martin", "author")
    assert ok is True
    assert all("martin" in b["author"].lower() for b in books)

@pytest.mark.xfail(reason="R6 not implemented yet.")
def test_search_by_isbn_exact(svc, catalog_fixture):
    ok, books = svc.search_books_in_catalog("9780201616224", "isbn")
    assert ok is True
    assert len(books) == 1 and books[0]["isbn"] == "9780201616224"
