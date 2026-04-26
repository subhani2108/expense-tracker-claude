# Plan: Profile Page Implementation (Step 4)

## Context

The `/profile` route currently returns a plain string placeholder. This step implements a fully designed profile page with hardcoded data — no database queries yet. The goal is to establish the complete UI layout before wiring up real backend data in Step 5.

## Files to Create

### `templates/profile.html`
New file extending `base.html`. Contains four sections:
1. **User info card** — avatar (initials), name, email, member-since date
2. **Summary stats row** — total spent (₹48,500), transaction count (24), top category (Food)
3. **Transaction history table** — 5 hardcoded expense rows with date, description, category badge, amount
4. **Category breakdown** — 4 categories with progress bars (Food 40%, Travel 25%, Bills 20%, Shopping 15%)

## Files to Change

### `app.py`
Replace the `/profile` stub with:
- Auth guard: if `session.get("user_id")` is None, `redirect(url_for("login"))`
- Hardcoded context dict passed to `render_template("profile.html", ...)`
- Hardcoded user data: name "Priya Sharma", email "priya@example.com", member since "January 2025"
- Hardcoded stats and transaction list

### `static/css/style.css`
Add profile-specific CSS classes using CSS variables:
- `.profile-header`, `.avatar`, `.user-info` — user card layout
- `.stat-grid`, `.stat-card`, `.stat-value`, `.stat-label` — summary stats
- `.transaction-list`, `.transaction-row` — transaction history
- `.category-list`, `.category-row`, `.category-bar-track`, `.category-bar` — category breakdown
- `.badge` base + `.badge-food`, `.badge-travel`, `.badge-bills`, `.badge-shopping` — category badges

## Design Rules

- All colours via CSS variables from `style.css` (e.g. `var(--ink)`, `var(--paper-card)`, `var(--accent)`)
- No inline styles or hex colour values in `profile.html`
- Category badges via CSS class — no inline colour
- Templates extend `base.html`, override `title` and `content` blocks
- No `<table>` elements — use CSS Grid/Flexbox for transaction list

## Hardcoded Data

```python
user = {"name": "Priya Sharma", "email": "priya@example.com", "member_since": "January 2025"}
stats = {"total_spent": "₹48,500", "transaction_count": "24", "top_category": "Food"}
transactions = [
    {"date": "26 Apr 2026", "description": "Swiggy order", "category": "Food", "amount": "₹320"},
    {"date": "25 Apr 2026", "description": "Metro pass", "category": "Travel", "amount": "₹150"},
    {"date": "24 Apr 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹2,400"},
    {"date": "22 Apr 2026", "description": "Amazon haul", "category": "Shopping", "amount": "₹1,850"},
    {"date": "20 Apr 2026", "description": "Monzo coffee", "category": "Food", "amount": "₹180"},
]
categories = [
    {"name": "Food", "amount": "₹19,400", "percent": 40, "class": "food"},
    {"name": "Travel", "amount": "₹12,125", "percent": 25, "class": "travel"},
    {"name": "Bills", "amount": "₹9,700", "percent": 20, "class": "bills"},
    {"name": "Shopping", "amount": "₹7,275", "percent": 15, "class": "shopping"},
]
```

## Verification

1. Run `python app.py` and navigate to `http://localhost:5001/profile` when logged out → should redirect to `/login`
2. Log in, visit `/profile` → should return HTTP 200 with full profile page
3. Inspect page — no hex colour values in `profile.html` source
4. Verify all 4 sections visible: user card, stats row, transaction table (5 rows), category breakdown (4 rows)
5. Check navbar shows "Sign out" link (logged-in state)