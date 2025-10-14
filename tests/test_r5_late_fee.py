"""
R5 — Late Fee Calculation

Spec:
- Due in 14 days.
- If overdue:
    * Days 1–7: $0.50/day
    * Day 8+:   $1.00/day
    * Cap at $15.00
- If not overdue: $0.00

We use the real temp SQLite DB (via fixtures) and simulate overdue by
adjusting the due_date of the active loan directly in the DB.
"""

import sqlite3
from datetime import datetime, timedelta

import pytest

def _set_due_date(db_path: str, patron_id: str, book_id: int, days_overdue: int):
    """
    Helper: set the due_date to 'days_overdue' days in the past (i.e., overdue).
    If days_overdue == 0, due_date is set to today (on time).
    """
    target_due = (datetime.now() - timedelta(days=days_overdue)).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE borrows
               SET due_date = ?
             WHERE patron_id = ?
               AND book_id = ?
               AND return_date IS NULL
            """,
            (target_due, patron_id, book_id),
        )
        conn.commit()

def test_late_fee_no_active_loan_returns_zero(svc):
    # No borrow exists for this combo
    result = svc.calculate_late_fee_for_book("123456", 9999)
    assert result["status"] in {"no_active_loan", "on_time"}
    assert result["fee_amount"] == 0.0
    assert result["days_overdue"] == 0

def test_late_fee_on_time_is_zero(svc, add_and_get_book_id, db_path):
    patron = "111111"
    book_id = add_and_get_book_id("T1", "A1", "5555555555551", 1)
    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok is True

    # Set due_date to today (not overdue)
    _set_due_date(db_path, patron, book_id, days_overdue=0)

    result = svc.calculate_late_fee_for_book(patron, book_id)
    assert result["status"] == "on_time"
    assert result["fee_amount"] == 0.0
    assert result["days_overdue"] == 0

def test_late_fee_seven_days_overdue(svc, add_and_get_book_id, db_path):
    patron = "222222"
    book_id = add_and_get_book_id("T2", "A2", "5555555555552", 1)
    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok is True

    _set_due_date(db_path, patron, book_id, days_overdue=7)

    result = svc.calculate_late_fee_for_book(patron, book_id)
    assert result["status"] == "late"
    assert result["days_overdue"] == 7
    # 7 * $0.50 = $3.50
    assert result["fee_amount"] == 3.50

def test_late_fee_eight_days_overdue_boundary(svc, add_and_get_book_id, db_path):
    patron = "333333"
    book_id = add_and_get_book_id("T3", "A3", "5555555555553", 1)
    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok is True

    _set_due_date(db_path, patron, book_id, days_overdue=8)

    result = svc.calculate_late_fee_for_book(patron, book_id)
    assert result["status"] == "late"
    assert result["days_overdue"] == 8
    # 7 * $0.50 + 1 * $1.00 = $4.50
    assert result["fee_amount"] == 4.50

def test_late_fee_cap_at_fifteen(svc, add_and_get_book_id, db_path):
    patron = "444444"
    book_id = add_and_get_book_id("T4", "A4", "5555555555554", 1)
    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok is True

    _set_due_date(db_path, patron, book_id, days_overdue=100)

    result = svc.calculate_late_fee_for_book(patron, book_id)
    assert result["status"] == "late"
    assert result["days_overdue"] >= 100
    assert result["fee_amount"] == 15.00  # capped
