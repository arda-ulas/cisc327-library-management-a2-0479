"""
R7 — Patron Status Report

We verify two representative shapes:
1) No history / no loans => zeros and empty lists
2) Some history with active loans including an overdue one =>
   counts make sense and total_late_fees > 0
"""
import sqlite3
from datetime import datetime, timedelta

def test_patron_status_no_history(svc):
    report = svc.get_patron_status_report("999999")  # never used in tests
    assert report["patron_id"] == "999999"
    assert report["counts"]["currently_borrowed"] == 0
    assert report["counts"]["history_total"] == 0
    assert report["total_late_fees"] == 0.0
    assert report["current_loans"] == []
    assert report["history"] == []

def test_patron_status_with_active_and_overdue(svc, add_and_get_book_id, db_path):
    patron = "777777"

    # Make two books
    b1 = add_and_get_book_id("TDD by Example", "Beck", "7000000000001", 1)
    b2 = add_and_get_book_id("Patterns of Enterprise", "Fowler", "7000000000002", 1)

    # Borrow both
    ok1, _ = svc.borrow_book_by_patron(patron, b1)
    ok2, _ = svc.borrow_book_by_patron(patron, b2)
    assert ok1 and ok2

    # Make b2 overdue by editing the DB: set due_date to 10 days in the past
    past_due = (datetime.now() - timedelta(days=10)).isoformat()
    past_borrow = (datetime.now() - timedelta(days=24)).isoformat()  # keep the 14-day rule coherent
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE borrows
               SET borrow_date = ?, due_date = ?
             WHERE patron_id = ? AND book_id = ?
            """,
            (past_borrow, past_due, patron, b2),
        )
        conn.commit()

    # Generate report
    report = svc.get_patron_status_report(patron)

    # Sanity on patron id
    assert report["patron_id"] == patron

    # Counts
    assert report["counts"]["currently_borrowed"] == 2
    assert report["counts"]["history_total"] >= 2  # at least the two borrows

    # There should be some fee for the overdue item
    assert report["total_late_fees"] > 0.0

    # Shape of current_loans entries
    cl = report["current_loans"]
    assert isinstance(cl, list) and len(cl) == 2
    for item in cl:
        assert {"book_id", "title", "author", "borrow_date", "due_date", "days_overdue", "late_fee"} <= set(item.keys())
