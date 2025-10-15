# test_r1_add_book_to_catalog.py

def test_r1_invalid_isbn_length(svc):
    """Boundary case: invalid ISBN length (fewer than 13 digits)."""
    ok, msg = svc.add_book_to_catalog("Refactoring", "Martin Fowler", "1234567890", 2)
    assert ok is False
    assert "isbn must be exactly 13 digits" in msg.lower()
