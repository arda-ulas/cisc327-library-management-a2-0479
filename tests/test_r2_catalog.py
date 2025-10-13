"""
R2 — Catalog display
Expectations:
- Page renders and shows table headers.
- Availability text shows "X/Y Available" when available_copies > 0.
"""
def test_catalog_page_renders(client):
    r = client.get("/catalog")
    assert r.status_code == 200
    assert b"Book Catalog" in r.data
    assert b"Title" in r.data and b"Author" in r.data and b"ISBN" in r.data

def test_catalog_shows_availability_text(svc, client, add_and_get_book_id):
    # Add a book with 2 copies and borrow 1 → expect "1/2 Available"
    book_id = add_and_get_book_id("The Pragmatic Programmer", "Andrew Hunt", "9780201616224", 2)
    ok, _ = svc.borrow_book_by_patron("123456", book_id)
    assert ok is True

    r = client.get("/catalog")
    assert r.status_code == 200
    assert b"1/2 Available" in r.data
