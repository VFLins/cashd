import os
import pytest
import asyncio
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from contextlib import contextmanager, AbstractContextManager
from typing import Literal, Generator, Callable, Iterator
from sqlalchemy import delete
from nicegui.testing import User, Screen
from cashd import auth
from cashd.const import PORT, ADMIN_ROUTES


def delete_user(user_id: int):
    """Removes an user from the database by PK 'Id'."""
    with auth.Session(bind=auth.DB_ENGINE) as ses:
        stmt = delete(auth.User).where(auth.User.Id == user_id)
        ses.execute(stmt)
        ses.commit()


def get_role_by_name(role_name: str) -> auth.Role:
    """Returns an `auth.Role` object from it's unique column 'RoleName'."""
    roles = auth.RoleSource()
    requested_role = [r for r in roles.current_data if r.RoleName == role_name][0]
    role = auth.Role()
    role.read(row_id=requested_role.Id)
    return role


@pytest.fixture
def mock_user() -> Callable[[str], AbstractContextManager[auth.User]]:
    """Yields a factory that creates a temporary user to test it's permission
    boundaries.
    """

    @contextmanager
    def _temp_user(
        role_name: Literal["Supervisor" | "Operador" | "Assistente" | "Desligado"],
    ) -> Iterator[auth.User]:
        role = get_role_by_name(role_name)
        username = os.urandom(16).hex()
        user = auth.store_login(role_id=role.Id, username=username, password="test")
        yield user
        delete_user(user_id=user.Id)

    yield _temp_user


def test_non_admin_redirect(local_ip: str):
    """Tests if the user is correctly being redirected from '/' to '/login' for
    authentication when connecting from IP address.
    """
    url = f"http://{local_ip}:{PORT}/"
    response = requests.get(url)
    assert response.status_code == 200
    assert "Faça login para acessar o sistema" in response.text
    assert response.url == f"{url}login"


def test_admin_redirect():
    """Tests if the admin is correctly *not* redirected from '/'. The admin is
    identified by the connection from 'http://127.0.0.1/' or 'http://localhost/'.
    """
    url = f"http://127.0.0.1:{PORT}/"
    response = requests.get(url)
    assert response.status_code == 200
    assert "Faça login para acessar o sistema" not in response.text
    assert response.url == url


@pytest.mark.parametrize("page", ["/", "/customer", "/stats", "/config", "/user"])
async def test_admin_access(page: str, user: User):
    """Tests if pages are correctly not being restricted from localhost."""
    # NiceGUI's user run from localhost by default
    await user.open(page)
    assert user.client.page.path == page


@pytest.mark.parametrize("user_role", ["Supervisor", "Operador", "Assistente"])
def test_forbidden_pages_redirect(
    user_role: str,
    mock_user: Callable[[str], AbstractContextManager[auth.User]],
    local_ip: str,
    screen: Screen,
):
    """Tests if users are correctly being redirected out of forbidden pages."""
    url = f"http://{local_ip}:{PORT}"
    with mock_user(user_role) as login:
        screen.selenium.get(url + "/login")
        screen.should_contain("Faça login para acessar o sistema")
        screen.type(Keys.TAB)  # to focus on the first input
        screen.type(login.Username)
        screen.type(Keys.TAB)  # to focus on the second input
        screen.type("test")
        screen.click("Entrar")
        restricted_pages = login.forbidden_pages() + list(ADMIN_ROUTES)
        for page in restricted_pages:
            screen.selenium.get(url + page)
            (
                WebDriverWait(driver=screen.selenium, timeout=5)
                .until(expected_conditions.url_to_be(url + "/"))
            )


def test_dismissed_user_restriction(screen: Screen, local_ip: str, mock_user: Callable[[str], AbstractContextManager[auth.User]]):
    """Test if the dismissed user is unable to login."""
    url = f"http://{local_ip}:{PORT}"
    with mock_user("Desligado") as login:
        screen.selenium.get(url + "/login")
        screen.should_contain("Faça login para acessar o sistema")
        screen.type(Keys.TAB)
        screen.type(login.Username)
        screen.type(Keys.TAB)
        screen.type("test")
        screen.click("Entrar")
        screen.should_contain("Este usuário não pode acessar o Cashd")


def test_dismissed_user_pages_redirect():
    """Test if the dismissed user is redirected to login page when dismissed (not implemented yet)."""
    pytest.skip("Not implemented yet.")
