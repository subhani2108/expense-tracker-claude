# Implementation Plan: Date Filter for Profile Page

## Context
The goal of this task is to implement a date-range filter on the user profile page. This allows users to narrow down their spending summary, transaction list, and category breakdown to a specific time period. This is a critical usability improvement for the Spendly expense tracker, moving from a simple "all-time" view to a dynamic analysis tool.

The implementation involves updating the `/profile` route in `app.py`, modifying three database query helpers in `database/queries.py`, adding a filter UI to `templates/profile.html`, and styling that UI in `static/css/profile.css`.

## Approach

### 1. Database Layer Updates (`database/queries.py`)
Modify the following functions to support optional date filtering:
- `get_summary_stats(user_id, date_from=None, date_to=None)`
- `get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)`
- `get_category_breakdown(user_id, date_from=None, date_to=None)`

**Logic:**
- Maintain the `WHERE user_id = ?` base filter.
- If both `date_from` and `date_to` are provided, append `AND date BETWEEN ? AND ?` to the query.
- Use parameterized queries for all inputs to prevent SQL injection.

### 2. Backend Logic (`app.py`)
Update the `profile()` view function to handle the filtering logic:

**Date Handling:**
- Extract `date_from` and `date_to` from `request.args`.
- Validate dates using `datetime.strptime(val, "%Y-%m-%d")`. If a `ValueError` occurs, treat the parameter as `None`.
- **Validation Constraint:** If `date_from > date_to`, flash `"Start date must be before end date."` and set both to `None`.
- Calculate preset dates in the backend to pass to the template:
  - **This Month**: First day of current month $\rightarrow$ today.
  - **Last 3 Months**: Today minus 3 months $\rightarrow$ today.
  - **Last 6 Months**: Today minus 6 months $\rightarrow$ today.
  - **All Time**: No filters.

**Data Flow:**
- Pass the validated `date_from` and `date_to` to the three updated database query helpers.
- Pass the calculated preset dates and the current active filter state back to the template for UI rendering.

### 3. Frontend implementation
**Template (`templates/profile.html`):**
- Insert a `.filter-bar` section above the summary stats.
- Include 4 preset buttons ("This Month", "Last 3 Months", "Last 6 Months", "All Time") as links using `url_for`.
- Implement a custom range form with two `<input type="date">` fields and an "Apply" button.
- Apply an `.active` class to the currently active preset based on the query parameters.

**Styling (`static/css/profile.css`):**
- Style the filter bar using `flexbox` for layout.
- Use CSS variables for the active state (`.preset-btn.active`) and input borders to maintain design consistency.
- Ensure no inline styles are used.

## Critical Files
- `Z:\expense-tracker-claude\app.py`
- `Z:\expense-tracker-claude\database\queries.py`
- `Z:\expense-tracker-claude\templates\profile.html`
- `Z:\expense-tracker-claude\static\css\profile.css`

## Verification Plan
1. **Default View**: Visit `/profile` without parameters. Verify it behaves exactly as before (All Time).
2. **Presets**:
   - Click "This Month", "Last 3 Months", and "Last 6 Months".
   - Verify URL query strings update correctly.
   - Verify the corresponding button is highlighted.
   - Verify that totals, transaction counts, and category percentages reflect only the selected period.
3. **Custom Range**:
   - Set a specific valid date range and click "Apply". Verify the data matches that range.
4. **Error Handling**:
   - Set `date_from` to a date *after* `date_to`. Verify the "Start date must be before end date." flash message appears and the view reverts to "All Time".
   - Manually enter a malformed date in the URL (e.g., `?date_from=abc`). Verify the app doesn't crash and falls back to "All Time".
5. **Edge Cases**:
   - Filter a period where the user has no expenses. Verify it shows `₹0.00` and an empty category list without crashing.
