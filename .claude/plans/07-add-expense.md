# Implementation Plan: Add Expense (Spec 07)

## Context
This feature allows authenticated users to record new expenses in the Spendly application. It converts the current placeholder route `/expenses/add` into a fully functional form that validates input and persists expenses to the database. This is a core part of the application's CRUD functionality, enabling users to build their spending history.

## Approach

### 1. Database Layer (`database/queries.py`)
- Implement `insert_expense(user_id, amount, category, date, description)`:
    - Use `get_db()` for connection.
    - execute parameterized `INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)`.
    - Call `conn.commit()` and `conn.close()`.

### 2. Backend Logic (`app.py`)
- Define a constant `EXPENSE_CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]`.
- Update `GET /expenses/add`:
    - Verify `session.get("user_id")`. Redirect to `/login` if missing.
    - Render `add_expense.html` passing `categories=EXPENSE_CATEGORIES`.
- Implement `POST /expenses/add`:
    - Verify authentication.
    - Extract form fields: `amount`, `category`, `date`, `description`.
    - **Validation**:
        - `amount`: Convert to float, must be `> 0`.
        - `category`: Must be present in `EXPENSE_CATEGORIES`.
        - `date`: Must be a valid date string (YYYY-MM-DD) via `datetime.strptime`.
    - **Sanitization**: Strip `description`; store as `None` if empty.
    - **Error Handling**: On failure, `flash()` error and re-render `add_expense.html` with current form values.
    - **Success**: Call `insert_expense`, `flash()` success, and redirect to `/profile`.

### 3. Frontend Implementation
- **Create `templates/add_expense.html`**:
    - Extend `base.html`.
    - Use `.auth-section` and `.auth-card` for consistent styling (matching `register.html`).
    - Form fields:
        - `amount`: `<input type="number" step="0.01" min="0.01" required>`
        - `category`: `<select>` populated from `categories` list.
        - `date`: `<input type="date" required>`
        - `description`: `<input type="text">`
    - Submit button: `<button class="btn-submit">Save Expense</button>`.
- **Modify `templates/profile.html`**:
    - Add a prominent "Add Expense" button/link that redirects to `/expenses/add`.
- **Modify `templates/base.html`**:
    - Add "Add Expense" link to the navbar, visible only when authenticated.

## Verification Plan
- **Auth Check**: Visit `/expenses/add` without logging in $\rightarrow$ expect redirect to `/login`.
- **Form Rendering**: Visit `/expenses/add` while logged in $\rightarrow$ expect 200 OK and correctly populated category dropdown.
- **Positive Path**: Submit a valid expense $\rightarrow$ expect redirect to `/profile`, success flash message, and new record in the transaction table.
- **Negative Path (Validation)**:
    - Submit zero/negative amount $\rightarrow$ expect error flash and form re-render with values.
    - Submit invalid category $\rightarrow$ expect error flash.
    - Submit invalid date $\rightarrow$ expect error flash.
- **Optionality**: Submit without a description $\rightarrow$ expect success and `NULL` stored in database for description.
- **UI Links**: Verify navbar link and profile page button both correctly navigate to the add expense form.

## Critical Files
- `database/queries.py`
- `app.py`
- `templates/add_expense.html`
- `templates/profile.html`
- `templates/base.html`
