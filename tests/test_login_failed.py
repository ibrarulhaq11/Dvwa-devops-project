import os
import re

import requests


BASE_URL = os.environ.get("DVWA_BASE_URL", "http://127.0.0.1:4280")
TOKEN_PATTERN = r'name=["\']user_token["\']\s+value=["\']([^"\']+)["\']'


def get_user_token(html):
    token_match = re.search(TOKEN_PATTERN, html)
    assert token_match, "Page did not include a user_token field."
    return token_match.group(1)


def reset_database(session):
    setup_page = session.get(f"{BASE_URL}/setup.php", timeout=10)
    setup_page.raise_for_status()

    response = session.post(
        f"{BASE_URL}/setup.php",
        data={
            "create_db": "Create / Reset Database",
            "user_token": get_user_token(setup_page.text),
        },
        allow_redirects=True,
        timeout=20,
    )
    response.raise_for_status()


def test_wrong_admin_password_is_rejected():
    session = requests.Session()
    reset_database(session)

    login_page = session.get(f"{BASE_URL}/login.php", timeout=10)
    login_page.raise_for_status()

    response = session.post(
        f"{BASE_URL}/login.php",
        data={
            "username": "admin",
            "password": "wrong-password-for-ci",
            "Login": "Login",
            "user_token": get_user_token(login_page.text),
        },
        allow_redirects=True,
        timeout=10,
    )

    assert response.status_code == 200
    assert "Login failed" in response.text
    assert "logout.php" not in response.text

def test_demo_wrong_admin_password_should_login_successfully():
    session = requests.Session()
    reset_database(session)

    login_page = session.get(f"{BASE_URL}/login.php", timeout=10)
    login_page.raise_for_status()

    response = session.post(
        f"{BASE_URL}/login.php",
        data={
            "username": "admin",
            "password": "wrong-password-for-ci",
            "Login": "Login",
            "user_token": get_user_token(login_page.text),
        },
        allow_redirects=True,
        timeout=10,
    )

    assert "You have logged in as 'admin'" in response.text
