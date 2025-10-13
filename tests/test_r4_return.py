"""
R4 — Return Book
Expectations:
- Verify book was borrowed by this patron.
- On return: increment available_copies, record return date, compute/display fee.
"""
import pytest
import sqlite3

def test_return_happy_path_updates_availability_and_sets_return_date(
    svc, add_and_get_book_id, db_path
):
    patron = "654321"
    book_id = add_and_get_book_id("Refactoring", "Martin Fowler", "9780201485677", 1)

    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok is True

    # Act: return
    ok2, msg2 = svc.return_book_by_patron(patron, book_id)
    assert ok2 is True

    # Verify: availability incremented and return_date set
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        b = conn.execute("SELECT available_copies, total_copies FROM books WHERE id = ?", (book_id,)).fetchone()
        assert b["available_copies"] == 1 and b["total_copies"] == 1
        loan = conn.execute(
            "SELECT return_date FROM borrows WHERE patron_id = ? AND book_id = ? ORDER BY id DESC LIMIT 1",
            (patron, book_id),
        ).fetchone()
        assert loan and loan["return_date"] is not None

def test_return_rejects_if_not_borrowed_by_patron(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("Design Patterns", "Gamma", "9780201633610", 1)
    ok, _ = svc.borrow_book_by_patron("111111", book_id)
    assert ok is True

    ok2, msg2 = svc.return_book_by_patron("222222", book_id)  # different patron
    assert ok2 is False
