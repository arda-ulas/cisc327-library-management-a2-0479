# Assignment 1 – Project Implementation Status
**Name:** Arda Ulas Ozdemir  
**Student ID:** 20370479  
**Group:** 3

## Environment
- **OS:** macOS 14.0
- **Python:** 3.11.4
- **Virtual environment:** `venv` (project-local)
- **Installed packages:** Flask 2.3.3, pytest 7.4.2

## Setup Steps (per instructions)
1. `python -m venv venv` → `source venv/bin/activate`  
2. `pip install -r requirements.txt`  
3. `python app.py` → open `http://localhost:5000`  
4. Updated banner text in `base.html` to show my name.  
5. Verified app runs locally (catalog page loads).

## Screenshots
- `banner.png` – banner shows my name on the running app.

## Implementation Status vs Requirements (R1–R7)

| Req | Area / Function (module) | Status | Notes (gaps / issues) |
|---|---|---|---|
| **R1** | Add Book — `add_book_to_catalog` (`library_service.py`) | **Complete** | Validates title ≤200 chars, author ≤100, ISBN exactly 13 digits (and unique), positive `total_copies`. Behavior matches spec. |
| **R2** | Catalog Display — `catalog()` (`routes/catalog_routes.py`) | **Complete** | Uses `get_all_books()` and renders `templates/catalog.html`; shows availability and borrow form when `available_copies > 0`. |
| **R3** | Borrowing — `borrow_book_by_patron` (`library_service.py`) | **Partial** | Patron ID must be 6 digits; availability enforced; records borrow. **Bug:** borrow limit uses `> 5` instead of `>= 5` → allows 6 books. |
| **R4** | Return Processing — `return_book_by_patron` (`library_service.py`) | **Missing** | Returns `(False, "not implemented")`. UI page exists but is informational only. |
| **R5** | Late Fee API — `calculate_late_fee_for_book` (`library_service.py`) | **Missing** | Not implemented; API route returns 501. Spec rules (14-day due; tiered daily fee; $15 cap) not enforced. |
| **R6** | Search — `search_books_in_catalog` (`library_service.py`) | **Missing** | Should support partial (title/author) and exact ISBN; currently returns empty list. |
| **R7** | Patron Status Report — `get_patron_status_report` (`library_service.py`) | **Missing** | Not implemented; no navigation link provided. |

**Consistency notes:**  
- `routes/api_routes.get_late_fee` docstring references **R4**, but Late Fee is **R5** in the spec.  
- `routes/search_routes.search_books` docstring references **R5**, but Search is **R6** in the spec.

## Unit Test Results
**Latest run:**  
`pytest -q`  
→ 12 passed, 8 xfailed, 1 xpassed

- **12 passed** – covers R1–R3 (validation, borrow logic, catalog view).  
- **8 xfail** – tests for R4–R7 written per TDD but functions not implemented yet.  
- **1 xpass** – confirms ISBN validation now behaves correctly.  
- No unexpected errors or failures.

## Planned Unit Tests (summary)
- **R1 Add Book:** valid add; invalid title/author lengths; ISBN not 13 digits; non-digit ISBN; duplicate ISBN; zero/negative `total_copies`.  
- **R2 Catalog:** verifies catalog render and availability display.  
- **R3 Borrow:** invalid patron IDs; non-existent book; unavailable book; **reject at 5 active borrows**; successful borrow updates availability.  
- **R4 Return:** returning unborrowed book; wrong patron; updates availability; sets return date; computes late fee.  
- **R5 Late Fee:** 0–7 days @ $0.50/day; > 7 days @ $1/day; cap at $15; boundary cases (7, 8, max).  
- **R6 Search:** title/author partial (case-insensitive); ISBN exact; empty term handling.  
- **R7 Patron Report:** correct aggregation of borrowed/returned items, late fees, and limits.
