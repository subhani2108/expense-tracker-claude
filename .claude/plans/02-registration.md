# Plan: Registration Feature (Step 02)

## Context
Implement user registration for Spendly. New users need to create an account with name, email, and password. The password must be securely hashed before storage. On success, the user is auto-logged in via session and redirected to the profile page.

The `register.html` template already exists with the correct form structure. The main work is adding the POST handler in `app.py` and enabling session handling.

## Dependencies
- 01-database-setup (users table already exists)

## Files Changed

### `app.py`
1. Import `request`, `redirect`, `session`, `flash` from Flask
2. Import `generate_password_hash` from `werkzeug.security`
3. Add `app.secret_key = "..."` (required for sessions)
4. Add POST handler for `/register`:
   - Get `name`, `email`, `password` from `request.form`
   - Validate all fields are non-empty → flash error if missing
   - Check email uniqueness via DB query → flash error if duplicate
   - Hash password with `generate_password_hash`
   - Insert user into DB, get `user_id`
   - Set `session["user_id"] = user_id`
   - Redirect to `/profile`

## Implementation Details

### POST `/register` handler logic:
```
1. Get form data: name, email, password
2. If any field empty → flash error, re-render register.html
3. Check if email exists in DB:
   SELECT id FROM users WHERE email = ?
   If exists → flash error "Email already registered", re-render register.html
4. Hash password: generate_password_hash(password)
5. Insert: INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)
6. Get lastrowid as user_id
7. Set session["user_id"] = user_id
8. Redirect to /profile
```

### DB query pattern (from existing db.py):
```python
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
if cursor.fetchone() is not None:
    # duplicate
cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
               (name, email, hashed))
user_id = cursor.lastrowid
conn.commit()
conn.close()
```

### Session handling:
- Add `app.secret_key = "spendly-secret-key-2026"` in app.py after Flask app creation
- Set `session["user_id"]` on successful registration

## Verification
1. Run `python app.py` — app starts without errors
2. Navigate to `http://localhost:5001/register` — form renders
3. Submit with empty fields → error flash shown
4. Submit with existing email (e.g., demo@spendly.com) → error flash shown
5. Submit with valid new data → redirected to `/profile`
6. Check that user was inserted in DB with hashed password
