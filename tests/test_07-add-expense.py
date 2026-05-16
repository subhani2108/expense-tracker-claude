import pytest
import os
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    # Use a separate database file for testing to avoid state pollution
    # and to ensure the database persists across connections (unlike :memory:)
    original_db_path = "spendly.db"
    test_db_path = "test_spendly.db"

    import database.db
    database.db.DATABASE_PATH = test_db_path

    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    with flask_app.app_context():
        init_db()
        yield flask_app

    # Cleanup after the test session
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass
    database.db.DATABASE_PATH = original_db_path

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    return client

class TestAddExpense:
    # --- Auth Guards ---

    def test_get_add_expense_unauthenticated_redirects_to_login(self, client):
        response = client.get('/expenses/add')
        assert response.status_code == 302
        assert response.location == '/login'

    def test_post_add_expense_unauthenticated_redirects_to_login(self, client):
        response = client.post('/expenses/add', data={
            'amount': '10.0',
            'category': 'Food',
            'date': '2026-05-16',
            'description': 'Test'
        })
        assert response.status_code == 302
        assert response.location == '/login'

    def test_get_add_expense_authenticated_renders_form(self, auth_client):
        response = auth_client.get('/expenses/add')
        assert response.status_code == 200
        assert b'<form' in response.data
        assert b'method="POST"' in response.data

        categories = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]
        for cat in categories:
            assert cat.encode() in response.data

    # --- Happy Path & Edge Cases ---

    def test_post_add_expense_valid_data_redirects_and_saves(self, auth_client):
        # Get user_id from session to verify DB
        with auth_client.application.app_context():
            # We can't easily get session from test_client without a request context,
            # but we know the first user created in auth_client fixture is id 1.
            user_id = 1

        payload = {
            'amount': '50.25',
            'category': 'Food',
            'date': '2026-05-16',
            'description': 'Lunch at Cafe'
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 302
        assert response.location == '/profile'

        # Verify DB side effect
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT amount, category, date, description FROM expenses WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row['amount'] == 50.25
        assert row['category'] == 'Food'
        assert row['date'] == '2026-05-16'
        assert row['description'] == 'Lunch at Cafe'

    def test_post_add_expense_no_description_saves_as_null(self, auth_client):
        user_id = 1
        payload = {
            'amount': '100.0',
            'category': 'Bills',
            'date': '2026-05-16',
            'description': ''
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 302
        assert response.location == '/profile'

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM expenses WHERE user_id = ? AND amount = 100.0", (user_id,))
        row = cursor.fetchone()
        conn.close()

        assert row['description'] is None

    def test_post_add_expense_whitespace_description_saves_as_null(self, auth_client):
        user_id = 1
        payload = {
            'amount': '100.0',
            'category': 'Bills',
            'date': '2026-05-16',
            'description': '   '
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 302

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM expenses WHERE user_id = ? AND amount = 100.0", (user_id,))
        row = cursor.fetchone()
        conn.close()

        assert row['description'] is None

    # --- Validation Errors ---

    @pytest.mark.parametrize("amount, expected_error", [
        ("", "Please enter a valid positive amount."),
        ("0", "Please enter a valid positive amount."),
        ("-10", "Please enter a valid positive amount."),
        ("abc", "Please enter a valid positive amount."),
    ])
    def test_post_add_expense_invalid_amount_shows_error(self, auth_client, amount, expected_error):
        payload = {
            'amount': amount,
            'category': 'Food',
            'date': '2026-05-16',
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 200
        assert expected_error.encode() in response.data

    def test_post_add_expense_invalid_category_shows_error(self, auth_client):
        payload = {
            'amount': '10.0',
            'category': 'InvalidCat',
            'date': '2026-05-16',
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 200
        assert b"Please select a valid category." in response.data

    @pytest.mark.parametrize("date_str, expected_error", [
        ("", "Please select a date."),
        ("2026-13-01", "Invalid date format."),
        ("16-05-2026", "Invalid date format."),
        ("not-a-date", "Invalid date format."),
    ])
    def test_post_add_expense_invalid_date_shows_error(self, auth_client, date_str, expected_error):
        payload = {
            'amount': '10.0',
            'category': 'Food',
            'date': date_str,
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload)

        assert response.status_code == 200
        assert expected_error.encode() in response.data
