from database.db import get_db
from datetime import datetime


def _fmt(amount):
    return f"₹{amount:,.2f}"


def _fmt_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%d %b %Y")


def get_user_by_id(user_id):
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


def get_summary_stats(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    transaction_count = row["count"]
    total_spent = row["total"]

    if transaction_count == 0:
        conn.close()
        return {"total_spent": "₹0.00", "transaction_count": 0, "top_category": "—"}

    cursor.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
    )
    top_row = cursor.fetchone()
    top_category = top_row["category"] if top_row else "—"

    conn.close()
    return {
        "total_spent": _fmt(total_spent),
        "transaction_count": transaction_count,
        "top_category": top_category
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"date": _fmt_date(row["date"]), "description": row["description"], "category": row["category"], "amount": _fmt(row["amount"])}
        for row in rows
    ]


def get_category_breakdown(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
    )
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
