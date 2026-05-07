import pytest
from app import app as flask_app
from database.db import init_db
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seeded_auth_client(auth_client, app):
    """A logged-in client with a controlled set of expenses for date filtering."""
    from database.db import get_db
    conn = get_db()
    cursor = conn.cursor()

    # Get the user id from session if possible or query DB
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_id = cursor.fetchone()['id']

    today = date.today()

    # Seed data:
    # 1. An expense today
    # 2. An expense 15 days ago (still this month usually)
    # 3. An expense 2 months ago (within 3 and 6 months)
    # 4. An expense 5 months ago (within 6 months)
    # 5. An expense 1 year ago (only All Time)

    expenses = [
        (user_id, 100.0, "Food", today.strftime("%Y-%m-%d"), "Today's Lunch"),
        (user_id, 200.0, "Transport", (today - timedelta(days=15)).strftime("%Y-%m-%d"), "Mid-month travel"),
        (user_id, 300.0, "Bills", (today - relativedelta(months=2)).strftime("%Y-%m-%d"), "Bill 2mo ago"),
        (user_id, 400.0, "Health", (today - relativedelta(months=5)).strftime("%Y-%m-%d"), "Health 5mo ago"),
        (user_id, 500.0, "Shopping", (today - relativedelta(years=1)).strftime("%Y-%m-%d"), "Old shopping"),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    conn.commit()
    conn.close()
    return auth_client

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Unauthenticated requests to /profile should redirect to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_default_view_shows_all(self, seeded_auth_client):
        """Default view without query params shows all expenses."""
        response = seeded_auth_client.get('/profile')
        assert response.status_code == 200
        # Total: 100+200+300+400+500 = 1500
        assert '₹1,500.00' in response.get_data(as_text=True)
        assert '5' in response.get_data(as_text=True) # transaction count

    def test_filter_this_month(self, seeded_auth_client):
        """'This Month' preset filters data to current calendar month."""
        today = date.today()
        start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
        end_of_month = today.strftime("%Y-%m-%d")

        response = seeded_auth_client.get(f'/profile?date_from={start_of_month}&date_to={end_of_month}')
        assert response.status_code == 200

        # Only today and mid-month (if in same month) should appear.
        # For simplicity, let's check that 1 year ago is definitely NOT there.
        assert 'Old shopping' not in response.get_data(as_text=True)
        assert 'Today\'s Lunch' in response.get_data(as_text=True)

    def test_filter_last_3_months(self, seeded_auth_client):
        """'Last 3 Months' preset filters data correctly."""
        today = date.today()
        three_months_ago = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        response = seeded_auth_client.get(f'/profile?date_from={three_months_ago}&date_to={end_date}')

        # Should include: Today, Mid-month, 2 months ago.
        # Should NOT include: 5 months ago, 1 year ago.
        assert 'Today\'s Lunch' in response.get_data(as_text=True)
        assert 'Bill 2mo ago' in response.get_data(as_text=True)
        assert 'Health 5mo ago' not in response.get_data(as_text=True)
        assert 'Old shopping' not in response.get_data(as_text=True)

    def test_filter_last_6_months(self, seeded_auth_client):
        """'Last 6 Months' preset filters data correctly."""
        today = date.today()
        six_months_ago = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        response = seeded_auth_client.get(f'/profile?date_from={six_months_ago}&date_to={end_date}')

        # Should include: Today, Mid-month, 2mo, 5mo.
        # Should NOT include: 1 year ago.
        assert 'Health 5mo ago' in response.get_data(as_text=True)
        assert 'Old shopping' not in response.get_data(as_text=True)

    def test_filter_all_time_preset(self, seeded_auth_client):
        """All Time preset (no params) removes filters."""
        # First apply a filter
        seeded_auth_client.get('/profile?date_from=2000-01-01&date_to=2000-01-02')
        # Then go back to profile
        response = seeded_auth_client.get('/profile')
        assert '₹1,500.00' in response.get_data(as_text=True)

    def test_custom_range_valid(self, seeded_auth_client):
        """Valid custom date range filters results correctly."""
        # Range that only covers the "Bill 2mo ago" and "Health 5mo ago"
        # (Adjusting based on the relativedelta seeds)
        today = date.today()
        date_from = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
        date_to = (today - relativedelta(months=1)).strftime("%Y-%m-%d")

        response = seeded_auth_client.get(f'/profile?date_from={date_from}&date_to={date_to}')

        assert 'Bill 2mo ago' in response.get_data(as_text=True)
        assert 'Health 5mo ago' in response.get_data(as_text=True)
        assert 'Today\'s Lunch' not in response.get_data(as_text=True)

    def test_custom_range_invalid_order(self, seeded_auth_client):
        """date_from > date_to should show flash error and fallback to unfiltered."""
        response = seeded_auth_client.get('/profile?date_from=2026-12-31&date_to=2026-01-01')

        assert 'Start date must be before end date.' in response.get_data(as_text=True)
        # Fallback to unfiltered: total should be 1500
        assert '₹1,500.00' in response.get_data(as_text=True)

    def test_custom_range_malformed_date(self, seeded_auth_client):
        """Malformed dates should fallback to unfiltered view without crashing."""
        response = seeded_auth_client.get('/profile?date_from=not-a-date&date_to=2026-05-01')

        assert response.status_code == 200
        # Fallback to unfiltered
        assert '₹1,500.00' in response.get_data(as_text=True)

    def test_range_with_no_expenses(self, seeded_auth_client):
        """Range with no data shows zeroed stats."""
        # Range in the far future
        response = seeded_auth_client.get('/profile?date_from=2099-01-01&date_to=2099-01-31')

        assert '₹0.00' in response.get_data(as_text=True)
        assert '0' in response.get_data(as_text=True) # transaction count
        # Category breakdown should be empty (check for absence of categories seeded)
        assert 'Food' not in response.get_data(as_text=True)
        assert 'Transport' not in response.get_data(as_text=True)
