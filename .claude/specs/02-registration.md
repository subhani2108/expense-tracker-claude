# Spec: Registration

## Overview
User registration for Spendly. Allows new users to create an account with a name, email, and password. The password is securely hashed using werkzeug before storage. On successful registration, the user is automatically logged in and redirected to the dashboard.

## Depends on
- 01-database-setup (users table must exist)

## Routes

- `GET /register` — Show registration form — public
- `POST /register` — Process registration form — public

## Database changes

- No new tables or columns
- Uses existing `users` table

## Templates

- **Create:** `templates/register.html`
- **Modify:** `templates/base.html` — no changes needed (already has flash messaging support)

## Files to change

- `app.py` — add POST handler for `/register`
- `static/style.css` — add registration form styles

## Files to create

- `templates/register.html`

## New dependencies

No new dependencies. Use `werkzeug.security` (already installed) for password hashing.

## Rules for implementation

- No SQLAlchemy or ORMs — use parameterized queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Validate email is unique before inserting
- Validate required fields (name, email, password)
- Use `request.form` to access form data
- Redirect to `/dashboard` on success
- Re-render form with error message on failure
- Use Flask's `flash()` for error messages
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values

## Definition of done

- [ ] `GET /register` renders the registration form
- [ ] `POST /register` with valid unique data creates a user and redirects to dashboard
- [ ] `POST /register` with duplicate email shows error message
- [ ] `POST /register` with missing fields shows error message
- [ ] Password is stored as a hash, not plaintext
- [ ] Successful registration auto-logs in the user (session set)
- [ ] Form submissions are rejected for empty required fields
