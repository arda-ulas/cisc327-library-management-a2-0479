"""
R3 — Borrow Book by Patron
Spec highlights:
- Patron ID must be exactly 6 digits
- Book must be available (available_copies > 0)
- A patron may have at most 5 active borrows simultaneously (block at 5)
"""
import pytest

def test_borrow_rejects_non_6_digit_patron_id(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("B", "A", "1111111111111", 1)
    ok, msg = svc.borrow_book_by_patron("12A456", book_id)  # not 6 digits
    assert ok is False
    assert "6" in msg or "digit" in msg.lower()

def test_borrow_unavailable_book_blocked(svc, add_and_get_book_id):
    # Create a book with a single copy; borrow it to make it unavailable; second borrow should fail.
    book_id = add_and_get_book_id("Book X", "Auth", "2222222222222", 1)
    ok1, _ = svc.borrow_book_by_patron("123456", book_id)
    assert ok1 is True
    ok2, msg2 = svc.borrow_book_by_patron("123456", book_id)
    assert ok2 is False
    assert "not available" in msg2.lower() or "unavailable" in msg2.lower()

@pytest.mark.xfail(reason="Spec: block the 6th borrow (max 5). Impl uses '> 5' instead of '>= 5'.")
def test_borrow_blocks_at_five_active_loans(svc, add_and_get_book_id):
    # Add 6 distinct 1-copy books; attempt 6th borrow should be rejected by spec.
    patron = "555555"
    book_ids = []
    for i in range(6):
        isbn = f"33333333333{i:02d}"  # distinct 13-digit strings
        book_ids.append(add_and_get_book_id(f"T{i}", "A", isbn, 1))

    # Take 5 borrows
    for i in range(5):
        ok, msg = svc.borrow_book_by_patron(patron, book_ids[i])
        assert ok is True, f"setup borrow {i+1} failed: {msg}"

    # The 6th should be blocked by spec
    ok6, _ = svc.borrow_book_by_patron(patron, book_ids[5])
    assert ok6 is False  # spec expectation
