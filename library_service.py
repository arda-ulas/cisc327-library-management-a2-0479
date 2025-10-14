"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_db_connection,
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    """
    # Normalize/trim
    title = (title or "").strip()
    author = (author or "").strip()
    isbn = (isbn or "").strip()

    # Title
    if not title:
        return False, "Title is required."
    if len(title) > 200:
        return False, "Title must be less than 200 characters."

    # Author
    if not author:
        return False, "Author is required."
    if len(author) > 100:
        return False, "Author must be less than 100 characters."

    # ISBN: exactly 13 digits (not just length)
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."

    # total_copies: positive integer
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    # Duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."

    # Insert (available_copies starts equal to total_copies)
    success = insert_book(title, author, isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    R4 — Process book return by a patron.

    Rules:
    - Patron ID must be exactly 6 digits.
    - There must be an active borrow (return_date IS NULL) for (patron_id, book_id).
    - On success: set return_date = now, increment available_copies.
    """
    # Validate patron
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Validate book and existence
    try:
        book_id = int(book_id)
    except Exception:
        return False, "Invalid book id."
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Try to set return_date on an active borrow for this patron/book
    now = datetime.now()
    updated = update_borrow_record_return_date(patron_id, book_id, now)
    if not updated:
        # No active borrow row for this patron & book
        return False, "No active borrow for this patron and book."

    # Increment availability
    if not update_book_availability(book_id, +1):
        return False, "Database error occurred while updating availability."

    return True, f'Returned "{book["title"]}".'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    R5 — Calculate late fees for a specific active loan of (patron_id, book_id).

    Rules from spec:
    - Loans are due in 14 days (already enforced on borrow).
    - If overdue:
        * Days 1–7 overdue: $0.50/day
        * Day 8+ overdue: $1.00/day
        * Total fee capped at $15.00
    Return:
        {
            'fee_amount': float,   # dollars
            'days_overdue': int,
            'status': 'on_time' | 'late' | 'no_active_loan'
        }
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'no_active_loan'}

    try:
        book_id = int(book_id)
    except Exception:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'no_active_loan'}

    # Find the active (unreturned) borrow for this patron/book
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT id, due_date
          FROM borrows
         WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
         ORDER BY id DESC
         LIMIT 1
        """,
        (patron_id, book_id),
    ).fetchone()
    conn.close()

    if not row:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'no_active_loan'}

    # Compute overdue days (based on local date difference)
    try:
        due_dt = datetime.fromisoformat(row["due_date"])
    except Exception:
        # If stored format is unexpected, be safe: no fee
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'no_active_loan'}

    today = datetime.now()
    days_overdue = max(0, (today.date() - due_dt.date()).days)

    if days_overdue == 0:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'on_time'}

    # Tiered fee with cap
    tier1_days = min(days_overdue, 7)
    tier2_days = max(days_overdue - 7, 0)
    fee = tier1_days * 0.50 + tier2_days * 1.00
    fee_capped = min(15.00, fee)

    # Round to 2 decimals for presentation
    fee_capped = round(fee_capped + 1e-9, 2)

    return {'fee_amount': fee_capped, 'days_overdue': days_overdue, 'status': 'late'}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    return {}
