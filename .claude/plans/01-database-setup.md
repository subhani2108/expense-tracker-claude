# Plan: Database Setup (Step 1)

## Context

The `database/db.py` file was a stub placeholder with no implementation. This step established the data layer foundation for Spendly. All future features (authentication, expense tracking) depend on this being correctly implemented.

## Changes

### 1. `database/db.py` — Implemented all three functions

**`get_db()`**
- Opens connection to `spendly.db` in project root
- Sets `row_factory = sqlite3.Row`
- Enables `PRAGMA foreign_keys = ON`
- Returns the connection

**`init_db()`**
- Uses `CREATE TABLE IF NOT EXISTS` for both tables
- `users` table: id, name, email (unique), password_hash, created_at (default datetime('now'))
- `expenses` table: id, user_id (FK → users.id), amount (REAL), category, date (TEXT YYYY-MM-DD), description (nullable), created_at (default datetime('now'))
- Safe to call multiple times

**`seed_db()`**
- Checks if `users` table has data → returns early if so (no duplication)
- Inserts demo user: name="Demo User", email="demo@spendly.com", password="demo123" (hashed with werkzeug.security.generate_password_hash)
- Inserts 8 sample expenses across all categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- Dates spread across April 2026, all YYYY-MM-DD format
- Uses parameterized queries exclusively

### 2. `app.py` — Added startup initialization

- Import `get_db`, `init_db`, `seed_db` from `database.db`
- Call `init_db()` and `seed_db()` inside `app.app_context()` before `app.run()`
- Database initializes on every app startup

## Critical Files

- `database/db.py` — implemented all functions
- `app.py` — added imports and startup calls

## Dependencies

- `sqlite3` (stdlib) — for database operations
- `werkzeug.security` (already in requirements.txt) — for password hashing

## Verification

1. Run `python app.py` — app starts without errors
2. Database file `spendly.db` created in project root
3. Both tables exist with correct schema
4. Re-running app does not duplicate seed data (idempotent check in seed_db)
5. Foreign key enforcement works
6. Demo user password is hashed (not plain text)