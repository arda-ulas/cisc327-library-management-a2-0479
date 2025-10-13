import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (CISC327-CMPE327-F25)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib
import sqlite3
import pytest

def _connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@pytest.fixture
def app_and_db(tmp_path, monkeypatch):
    """
    Point the application's SQLite database to a temp file,
    then create the Flask app via the factory (which initializes & seeds data).
    Returns (app, db_path) so tests can query the DB when they need a book_id.
    """
    db_path = str(tmp_path / "test_library.db")

    # Redirect the database module's DATABASE constant BEFORE app creation
    database = importlib.import_module("database")
    monkeypatch.setattr(database, "DATABASE", db_path)

    app_module = importlib.import_module("app")
    app = app_module.create_app()          # initializes DB + sample data
    app.config.update(TESTING=True)

    return app, db_path

@pytest.fixture
def client(app_and_db):
    app, _ = app_and_db
    return app.test_client()

@pytest.fixture
def db_path(app_and_db):
    _, path = app_and_db
    return path

@pytest.fixture
def svc():
    """Business-logic surface under test (R1, R3 today)."""
    return importlib.import_module("library_service")

# --- Small helpers for tests that need a book_id -----------------------------

@pytest.fixture
def get_book_id(db_path):
    def _by_isbn(isbn: str) -> int | None:
        with _connect(db_path) as conn:
            row = conn.execute("SELECT id FROM books WHERE isbn = ?", (isbn,)).fetchone()
            return row["id"] if row else None
    return _by_isbn

@pytest.fixture
def add_and_get_book_id(svc, get_book_id):
    def _make(title: str, author: str, isbn: str, total_copies: int = 1) -> int:
        ok, msg = svc.add_book_to_catalog(title, author, isbn, total_copies)
        assert ok, f"setup failed to add book: {msg}"
        book_id = get_book_id(isbn)
        assert book_id is not None, "book id not found after insert"
        return book_id
    return _make
