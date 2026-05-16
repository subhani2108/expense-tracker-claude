from database.db import get_db
from datetime import datetime


def _fmt(amount):
    return f"₹{amount:,.2f}"


def _fmt_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%d %b %Y")


def _apply_date_filters(query, params, date_from, date_to):
    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    elif date_from:
        query += " AND date >= ?"
        params.append(date_from)
    elif date_to:
        query += " AND date <= ?"
        params.append(date_to)
    return query, params


def get_user_by_id(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    member_since = created.strftime("%B %Y")
    return {"name": row["name"], "email": row["email"], "member_since": member_since}


def get_summary_stats(user_id: int, date_from: str = None, date_to: str = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ?"
    params = [user_id]
    query, params = _apply_date_filters(query, params, date_from, date_to)

    cursor.execute(query, params)
    row = cursor.fetchone()
    transaction_count = row["count"]
    total_spent = row["total"]

    if transaction_count == 0:
        conn.close()
        return {"total_spent": "₹0.00", "transaction_count": 0, "top_category": "—"}

    query_top = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
    params_top = [user_id]
    query_top, params_top = _apply_date_filters(query_top, params_top, date_from, date_to)

    query_top += " GROUP BY category ORDER BY total DESC"
    cursor.execute(query_top, params_top)
    top_row = cursor.fetchone()
    top_category = top_row["category"] if top_row else "—"

    conn.close()
    return {
        "total_spent": _fmt(total_spent),
        "transaction_count": transaction_count,
        "top_category": top_category
    }


def get_recent_transactions(user_id: int, limit: int = 10, date_from: str = None, date_to: str = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT date, description, category, amount FROM expenses WHERE user_id = ?"
    params = [user_id]
    query, params = _apply_date_filters(query, params, date_from, date_to)

    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [
        {"date": _fmt_date(row["date"]), "description": row["description"], "category": row["category"], "amount": _fmt(row["amount"])}
        for row in rows
    ]


def get_category_breakdown(user_id: int, date_from: str = None, date_to: str = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
    params = [user_id]
    query, params = _apply_date_filters(query, params, date_from, date_to)

    query += " GROUP BY category ORDER BY total DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    grand_total = sum(row["total"] for row in rows)

    breakdown = []
    raw_pcts = []
    for row in rows:
        pct = round((row["total"] / grand_total) * 100) if grand_total > 0 else 0
        raw_pcts.append(pct)
        breakdown.append({
            "name": row["category"],
            "amount": _fmt(row["total"]),
            "pct": pct
        })

    rounding_diff = 100 - sum(raw_pcts)
    if rounding_diff != 0 and breakdown:
        breakdown[0]["pct"] += rounding_diff

    return breakdown


def insert_expense(user_id: int, amount: float, category: str, date: str, description: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description)
        )
        conn.commit()

