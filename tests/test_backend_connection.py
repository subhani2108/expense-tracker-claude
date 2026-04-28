import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, seed_db, get_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)


@pytest.fixture
def fresh_db(tmp_path):
    """Use a temp database for each test."""
    import database.db
    old_path = database.db.DATABASE_PATH
    database.db.DATABASE_PATH = str(tmp_path / "test.db")
    init_db()
    seed_db()
    yield
    database.db.DATABASE_PATH = old_path


class TestGetUserById:
    def test_returns_correct_user_data(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        result = get_user_by_id(user_id)
        assert result["name"] == "Demo User"
        assert result["email"] == "demo@spendly.com"
        assert "member_since" in result
        assert " " in result["member_since"]

    def test_non_existent_id_returns_none(self, fresh_db):
        result = get_user_by_id(9999)
        assert result is None


class TestGetSummaryStats:
    def test_returns_correct_stats_for_seed_user(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        stats = get_summary_stats(user_id)
        assert stats["transaction_count"] == 8
        assert "total_spent" in stats
        assert stats["top_category"] == "Bills"

    def test_returns_zeros_for_user_with_no_expenses(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Empty User", "empty@test.com", "hash")
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        stats = get_summary_stats(user_id)
        assert stats["transaction_count"] == 0
        assert stats["total_spent"] == "₹0.00"
        assert stats["top_category"] == "—"


class TestGetRecentTransactions:
    def test_returns_transactions_newest_first(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        txs = get_recent_transactions(user_id)
        assert len(txs) == 8
        dates = [tx["date"] for tx in txs]
        assert dates == sorted(dates, reverse=True)

    def test_returns_empty_list_for_user_with_no_expenses(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Empty User", "empty2@test.com", "hash")
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        txs = get_recent_transactions(user_id)
        assert txs == []

    def test_respects_limit(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        txs = get_recent_transactions(user_id, limit=3)
        assert len(txs) == 3


class TestGetCategoryBreakdown:
    def test_returns_all_categories_for_seed_user(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        breakdown = get_category_breakdown(user_id)
        assert len(breakdown) == 7
        pcts = [cat["pct"] for cat in breakdown]
        assert sum(pcts) == 100

    def test_returns_ordered_by_amount_desc(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()["id"]
        conn.close()

        breakdown = get_category_breakdown(user_id)
        amounts = [float(cat["amount"].replace("₹", "").replace(",", "")) for cat in breakdown]
        assert amounts == sorted(amounts, reverse=True)
        assert len(breakdown) == 7

    def test_returns_empty_list_for_user_with_no_expenses(self, fresh_db):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Empty User", "empty3@test.com", "hash")
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        breakdown = get_category_breakdown(user_id)
        assert breakdown == []
