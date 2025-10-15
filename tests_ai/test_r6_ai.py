# test_r6_search_catalog.py

def test_r6_search_by_title(svc):
    svc.add_book_to_catalog("Refactoring", "Martin Fowler", "1616161616161", 1)
    results = svc.search_books_in_catalog("factor", "title")
    assert any("Refactoring" in b["title"] for b in results)

def test_r6_search_by_author(svc):
    svc.add_book_to_catalog("Clean Architecture", "Robert Martin", "1717171717171", 1)
    results = svc.search_books_in_catalog("martin", "author")
    assert any("Robert Martin" in b["author"] for b in results)

def test_r6_search_by_isbn(svc):
    svc.add_book_to_catalog("Domain-Driven Design", "Eric Evans", "1818181818181", 1)
    results = svc.search_books_in_catalog("1818181818181", "isbn")
    assert len(results) == 1
    assert results[0]["title"] == "Domain-Driven Design"

def test_r6_invalid_search_type(svc):
    results = svc.search_books_in_catalog("anything", "genre")
    assert results == []

def test_r6_empty_search_term(svc):
    results = svc.search_books_in_catalog("", "title")
    assert results == []