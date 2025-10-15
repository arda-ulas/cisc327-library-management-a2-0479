# test_r7_patron_status_report.py

import sqlite3
from datetime import datetime, timedelta

def test_r7_valid_report(svc, add_and_get_book_id):
    patron = "555555"  # use a patron not present in seed data
    book_id = add_and_get_book_id("Report Book", "Author", "1919191919191", 1)
    svc.borrow_book_by_patron(patron, book_id)
    report = svc.get_patron_status_report(patron)
    assert report["patron_id"] == patron
    assert report["counts"]["currently_borrowed"] == 1
    assert isinstance(report["current_loans"], list)

def test_r7_invalid_patron_id(svc):
    report = svc.get_patron_status_report("12x456")
    assert "error" in report
    assert "invalid patron id" in report["error"].lower()

def test_r7_late_fee_in_report(svc, add_and_get_book_id, db_path):
    book_id = add_and_get_book_id("Late Report Book", "Author", "2020202020202", 1)
    svc.borrow_book_by_patron("654321", book_id)
    due_date = datetime.now() - timedelta(days=8)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE borrows SET due_date = ? WHERE book_id = ? AND patron_id = ? AND return_date IS NULL",
                     (due_date.isoformat(), book_id, "654321"))
    report = svc.get_patron_status_report("654321")
    assert report["total_late_fees"] > 0
    assert report["current_loans"][0]["days_overdue"] >= 8
