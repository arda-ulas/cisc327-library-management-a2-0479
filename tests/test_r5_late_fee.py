"""
R5 — Late fee calculation
Spec (typical): 14-day due window; 0–7 days overdue @ $0.50/day; >7 days @ $1/day; max $15/book.
We create a borrow and then backdate the borrow_date to simulate overdues.
"""
import pytest
import sqlite3
from datetime import datetime, timedelta

def _set_borrow_date(db_path, patron_id, book_id, days_ago: int):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE borrows SET borrow_date = ? WHERE patron_id = ? AND book_id = ?",
            ((datetime.utcnow() - timedelta(days=days_ago)).isoformat(), patron_id, book_id),
        )
        conn.commit()

@pytest.mark.xfail(reason="R5 not implemented yet.")
def test_late_fee_on_time_is_zero(svc, add_and_get_book_id, db_path):
    patron, book_id = "777777", add_and_get_book_id("Book A", "Auth", "9990000000000", 1)
    assert svc.borrow_book_by_patron(patron, book_id)[0] is True
    _set_borrow_date(db_path, patron, book_id, days_ago=10)  # within 14-day window
    ok, fee = svc.calculate_late_fee_for_book(patron, book_id)
    assert ok and fee == 0.0

@pytest.mark.xfail(reason="R5 not implemented yet.")
def test_late_fee_boundary_and_cap(svc, add_and_get_book_id, db_path):
    patron, book_id = "888888", add_and_get_book_id("Book B", "Auth", "9990000000001", 1)
    assert svc.borrow_book_by_patron(patron, book_id)[0] is True

    # 15 days late → 1 day overdue beyond 14; expect $0.50
    _set_borrow_date(db_path, patron, book_id, days_ago=15)
    ok, fee = svc.calculate_late_fee_for_book(patron, book_id)
    assert ok and 0.49 <= fee <= 0.51

    # Very late → should cap at $15
    _set_borrow_date(db_path, patron, book_id, days_ago=60)
    ok2, fee2 = svc.calculate_late_fee_for_book(patron, book_id)
    assert ok2 and fee2 == 15.00
