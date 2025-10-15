# test_r1_add_book_to_catalog.py

def test_r1_add_valid_book(svc):
    ok, msg = svc.add_book_to_catalog("Clean Code", "Robert Martin", "1234567890123", 3)
    assert ok is True
    assert "successfully added" in msg.lower()

def test_r1_missing_title(svc):
    ok, msg = svc.add_book_to_catalog("", "Robert Martin", "1234567890123", 3)
    assert ok is False
    assert "title is required" in msg.lower()

def test_r1_long_title(svc):
    long_title = "A" * 201
    ok, msg = svc.add_book_to_catalog(long_title, "Robert Martin", "1234567890123", 3)
    assert ok is False
    assert "title must be less than" in msg.lower()

def test_r1_invalid_isbn_length(svc):
    ok, msg = svc.add_book_to_catalog("Refactoring", "Martin Fowler", "1234567890", 2)
    assert ok is False
    assert "isbn must be exactly 13 digits" in msg.lower()

def test_r1_duplicate_isbn(svc):
    svc.add_book_to_catalog("1984", "George Orwell", "9999999999999", 1)
    ok, msg = svc.add_book_to_catalog("Animal Farm", "George Orwell", "9999999999999", 1)
    assert ok is False
    assert "already exists" in msg.lower()

def test_r1_negative_total_copies(svc):
    ok, msg = svc.add_book_to_catalog("Test Book", "Author", "1111111111111", -1)
    assert ok is False
    assert "positive integer" in msg.lower()