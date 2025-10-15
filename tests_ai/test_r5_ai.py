# test_r5_late_fee.py

import sqlite3
from datetime import datetime, timedelta

def test_r5_no_active_loan_fee(svc):
    result = svc.calculate_late_fee_for_book("123456", 9999)
    assert result["fee_amount"] == 0.0
    assert result["status"] == "no_active_loan"

def test_r5_on_time_loan_fee(svc, add_and_get_book_id):
    book_id = add_and_get_book_id("On Time", "Author", "1313131313131", 1)
    svc.borrow_book_by_patron("123456", book_id)
    result = svc.calculate_late_fee_for_book("123456", book_id)
    assert result["fee_amount"] == 0.0
    assert result["status"] == "on_time"

def test_r5_overdue_fee_under_7_days(svc, add_and_get_book_id, db_path):
    book_id = add_and_get_book_id("Late Book", "Author", "1414141414141", 1)
    svc.borrow_book_by_patron("123456", book_id)
    overdue_days = 5
    due_date = datetime.now() - timedelta(days=overdue_days)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE borrows SET due_date = ? WHERE book_id = ? AND patron_id = ? AND return_date IS NULL",
                     (due_date.isoformat(), book_id, "123456"))
    result = svc.calculate_late_fee_for_book("123456", book_id)
    assert result["fee_amount"] == 2.5
    assert result["days_overdue"] == overdue_days
def test_r5_overdue_fee_over_7_days(svc, add_and_get_book_id, db_path):
    book_id = add_and_get_book_id("Very Late Book", "Author", "1515151515151", 1)
    svc.borrow_book_by_patron("123456", book_id)
    overdue_days = 10
    due_date = datetime.now() - timedelta(days=overdue_days)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE borrows SET due_date = ? WHERE book_id = ? AND patron_id = ? AND return_date IS NULL",
                     (due_date.isoformat(), book_id, "123456"))
    result = svc.calculate_late_fee_for_book("123456", book_id)
    assert result["fee_amount"] == 6.5
    assert result["days_overdue"] == overdue_days
