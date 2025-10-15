# test_r4_return_book.py

def test_r4_valid_return(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Returnable Book", "Author", "9999999999999", 1)
    svc.borrow_book_by_patron("123456", book_id)
    ok, msg = svc.return_book_by_patron("123456", book_id)
    assert ok is True
    assert "returned" in msg.lower()

def test_r4_invalid_patron_id(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Book", "Author", "1010101010101", 1)
    svc.borrow_book_by_patron("123456", book_id)
    ok, msg = svc.return_book_by_patron("12x456", book_id)
    assert ok is False
    assert "invalid patron id" in msg.lower()

def test_r4_no_active_borrow(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Never Borrowed", "Author", "1212121212121", 1)
    ok, msg = svc.return_book_by_patron("123456", book_id)
    assert ok is False
    assert "no active borrow" in msg.lower()
