# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly — A Flask-based personal expense tracking web application. Still in development with placeholder routes for upcoming features.

## Commands

```bash
# Run the application
python app.py

# Install dependencies
pip install -r requirements.txt
```

## Architecture

- **app.py**: Main Flask application with routes for authentication (login, register, logout) and expense CRUD operations (add, edit, delete). Currently only auth routes render templates; expense routes return placeholder strings.
- **database/db.py**: Database layer (stub). Should implement `get_db()`, `init_db()`, and `seed_db()` for SQLite with row_factory and foreign keys enabled.
- **templates/**: Jinja2 templates using template inheritance (`base.html` → page templates).
- **static/**: CSS (`style.css`) and JavaScript (`main.js` — currently empty, to be populated as features are built).

## Development Notes

- The app runs on port 5001 with debug mode enabled.
- SQLite database file (`expense_tracker.db`) is gitignored and created at runtime.
- Uses Indian Rupee (₹) as the currency symbol.
