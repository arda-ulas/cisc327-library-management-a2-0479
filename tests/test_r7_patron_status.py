"""
R7 — Patron status report
Expectations (typical from spec):
- Report includes current loans (with due dates), total late fees, counts, and borrowing history.
"""
import pytest
import sqlite3
from datetime import datetime, timedelta

@pytest.mark.xfail(reason="R7 not implemented yet.")
def test_patron_status_report_structure(svc, add_and_get_book_id, db_path):
    patron = "999999"
    b1 = add_and_get_book_id("Book 1", "Auth", "7777777777777", 1)
    b2 = add_and_get_book_id("Book 2", "Auth", "7777777777778", 1)
    assert svc.borrow_book_by_patron(patron, b1)[0] is True
    assert svc.borrow_book_by_patron(patron, b2)[0] is True

    # Backdate one borrow to simulate overdue
    with sqlite3.connect(db_path) as conn:
        past = (datetime.utcnow() - timedelta(days=25)).isoformat()
        conn.execute("UPDATE borrows SET borrow_date = ? WHERE patron_id = ? AND book_id = ?", (past, patron, b1))
        conn.commit()

    ok, report = svc.get_patron_status_report(patron)
    assert ok is True
    # Expected shape (example; adapt to your spec keys)
    assert set(report.keys()) >= {"patron_id", "current_loans", "total_late_fees", "counts"}
    assert isinstance(report["current_loans"], list)
