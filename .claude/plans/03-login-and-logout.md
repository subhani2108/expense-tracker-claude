# Plan: Login and Logout (Step 03)

## Context
Implementing user login and logout functionality for Spendly. This extends the registration feature (Step 02) by allowing existing users to authenticate. Users who already have an account can log in with email and password; logged-in users can log out.

## Changes

### 1. `app.py` — Modify

**Add POST handler for `/login`** (combined with GET in `login()`):
- Get `email` and `password` from `request.form`
- Query `users` table for email using parameterized query
- If user not found → `flash("Invalid email or password.", "error")` → re-render `login.html`
- If user found, use `werkzeug.security.check_password_hash(password_hash, password)`
- If password mismatch → `flash("Invalid email or password.", "error")` → re-render `login.html`
- On success → set `session["user_id"] = user_id` → redirect to `/profile`
- On GET request: if `session.get("user_id")` is set, redirect to `/profile`

**Complete `logout()` GET handler**:
- Call `session.pop("user_id", None)` before redirect
- Redirect to `/login`

### 2. `templates/login.html` — Modify

- Change `{% if error %}` block to use flash messaging: `{% with messages = get_flashed_messages(with_categories=true) %}`
- Replace `{{ error }}` with proper flash message display

## Verification
1. Run `python app.py`
2. Test `GET /login` — should show login form
3. Test `POST /login` with demo@spendly.com / demo123 — should redirect to /profile
4. Test `POST /login` with wrong password — should show flash error
5. Test `POST /login` with non-existent email — should show flash error
6. Test `GET /logout` — should clear session and redirect to /login
7. Visit `/login` while logged in — should redirect to `/profile`
