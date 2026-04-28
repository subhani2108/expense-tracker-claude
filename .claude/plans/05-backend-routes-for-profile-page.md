# Plan: Backend Routes for Profile Page (Step 5)

## Context
The `/profile` route currently returns hardcoded dummy data for "Priya Sharma". Every logged-in user sees the same static content. This step wires the profile page to real database queries so each user sees their own data.

## What to build

### 1. Create `database/queries.py`
Four pure query functions, each opening its own DB connection and closing it before returning:

| Function | SQL | Returns |
|---|---|---|
| `get_user_by_id(user_id)` | `SELECT name, email, created_at FROM users WHERE id = ?` | `dict` or `None` |
| `get_summary_stats(user_id)` | Aggregates `SUM(amount)`, `COUNT(*)`, `MAX BY category sum` | `dict` with `total_spent` (₹ formatted), `transaction_count`, `top_category` |
| `get_recent_transactions(user_id, limit=10)` | `SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?` | `list[dict]` |
| `get_category_breakdown(user_id)` | Groups by category, sums amounts, computes percentage | `list[dict]` with `name`, `amount` (₹ formatted), `pct` (integers summing to 100) |

### 2. Modify `app.py` — `profile()` route
Replace hardcoded dicts with calls to the four query functions. Handle case where user is not found (redirect to login).

### 3. Modify `templates/profile.html`
Currency values already use `₹` — verify formatting helpers add ₹ prefix and comma-separated decimals.

### 4. Create `tests/test_backend_connection.py`
Unit tests for each query function + route tests for `/profile`.

### 5. Create `tests/__init__.py`

## Files

| Action | File |
|---|---|
| Create | `database/queries.py` |
| Create | `tests/__init__.py` |
| Create | `tests/test_backend_connection.py` |
| Modify | `app.py` — `profile()` function |
| Modify | `templates/profile.html` — verify ₹ usage |

## Verification
1. Run the app: `python app.py`
2. Log in as demo user (`demo@spendly.com` / `demo123`)
3. Visit `/profile` — should show "Demo User", real expense data
4. Register a new user and visit `/profile` — should show ₹0.00, 0 transactions, empty breakdown
5. Run tests: `python -m pytest tests/test_backend_connection.py -v`
