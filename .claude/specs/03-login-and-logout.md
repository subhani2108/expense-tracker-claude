# Spec: Login and Logout

## Overview
User authentication for Spendly via login and logout. Users who already have an account (created in Step 2) can log in with their email and password. On successful login, they are redirected to their profile page. Logged-in users can log out, which clears their session.

## Depends on
- 01-database-setup (users table must exist with password_hash)
- 02-registration (users must be able to register; login extends that flow)

## Routes

- `GET /login` — Show login form — public
- `POST /login` — Authenticate user — public
- `GET /logout` — Clear session and redirect — logged-in only

## Database changes

No new tables or columns. Uses existing `users` table.

## Templates

- **Create:** none
- **Modify:** `templates/login.html` — add login POST form (already exists as placeholder)

## Files to change

- `app.py` — add POST handler for `/login`, complete GET handler, complete `logout` route
- `templates/login.html` — add form with POST method and CSRF-safe inputs

## Files to create

None.

## New dependencies

No new dependencies. Use `werkzeug.security.check_password_hash` for password verification.

## Rules for implementation

- No SQLAlchemy or ORMs — use parameterized queries only
- Passwords verified with `werkzeug.security.check_password_hash`
- Validate credentials before setting session
- Redirect to `/profile` on success
- Re-render form with error message on failure
- Use Flask's `flash()` for error messages
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values
- Login form must be a proper POST form (not GET)
- Set `session["user_id"]` on successful login
- Clear `session["user_id"]` on logout
- Always call `session.pop("user_id", None)` before `redirect` in logout to avoid `PendingPopupError`

## Definition of done

- [ ] `GET /login` renders the login form
- [ ] `POST /login` with correct email/password redirects to profile
- [ ] `POST /login` with wrong password shows error message
- [ ] `POST /login` with non-existent email shows error message
- [ ] Successful login sets `session["user_id"]`
- [ ] `GET /logout` clears session and redirects to `/login`
- [ ] Flash messages display correctly on login failure
- [ ] Logged-in users cannot access `/login` (redirect to `/profile`)
