# test_r3_borrow_book.py

def test_r3_valid_borrow(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Borrowable Book", "Author", "5555555555555", 1)
    ok, msg = svc.borrow_book_by_patron("123456", book_id)
    assert ok is True
    assert "successfully borrowed" in msg.lower()

def test_r3_invalid_patron_id(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Book", "Author", "6666666666666", 1)
    ok, msg = svc.borrow_book_by_patron("abc123", book_id)
    assert ok is False
    assert "invalid patron id" in msg.lower()

def test_r3_borrow_unavailable_book(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Unavailable", "Author", "7777777777777", 1)
    svc.borrow_book_by_patron("123456", book_id)
    ok, msg = svc.borrow_book_by_patron("654321", book_id)
    assert ok is False
    assert "not available" in msg.lower()

def test_r3_patron_borrow_limit(svc, add_and_get_book_id):
    for i in range(5):
        isbn = f"88888888888{i:02d}"
        book_id = add_and_get_book_id(f"Book {i}", "Author", isbn, 1)
        svc.borrow_book_by_patron("999999", book_id)
    extra_book_id = add_and_get_book_id("Extra Book", "Author", "8888888888855", 1)
    ok, msg = svc.borrow_book_by_patron("999999", extra_book_id)
    assert ok is False
    assert "maximum borrowing limit" in msg.lower()