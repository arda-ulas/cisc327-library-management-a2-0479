# test_r2_view_catalog.py

def test_r2_catalog_shows_all_books(svc):
    svc.add_book_to_catalog("Book A", "Author A", "1111111111111", 2)
    svc.add_book_to_catalog("Book B", "Author B", "2222222222222", 1)
    books = svc.get_all_books()
    titles = [b["title"] for b in books]
    assert "Book A" in titles
    assert "Book B" in titles

def test_r2_available_copies_match_total_on_add(svc):
    svc.add_book_to_catalog("Book C", "Author C", "3333333333333", 4)
    book = next(b for b in svc.get_all_books() if b["isbn"] == "3333333333333")
    assert book["available_copies"] == 4

def test_r2_unavailable_book_status(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Unavailable Book", "Author", "4444444444444", 1)
    svc.borrow_book_by_patron("123456", book_id)
    book = next(b for b in svc.get_all_books() if b["id"] == book_id)
    assert book["available_copies"] == 0