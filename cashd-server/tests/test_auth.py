import pytest
import asyncio
import requests
from sqlalchemy import delete
from nicegui.testing import User
from cashd import auth
from cashd.const import PORT


def delete_user(user_id: int):
    """Removes an user from the database by PK 'Id'."""
    with auth.Session(bind=auth.DB_ENGINE) as ses:
        stmt = delete(auth.User).where(User.Id == user_id)
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
def operator_user():
    """Creates an operator user to test it's permission boundaries.
    username: __test_operator__
    password: test
    """
    operator_role = get_role_by_name("Operador")
    user = auth.store_login(
        role_id=operator_role.Id,
        username="__test_operator__",
        password="test"
    )
    yield user
    delete_user(user_id=user.Id)


def test_non_admin_redirect(local_ip: str):
    """Tests if the user is correctly being redirected from '/' to '/login' for
    authentication.
    """
    if local_ip == "127.0.0.1":
        pytest.skip("No local network IP found.")
    url = f"http://{local_ip}:{PORT}"
    response = requests.get(url)
    assert response.status_code == 200
    assert "Faça login para acessar o sistema" in response.text
    assert response.url == f"http://{local_ip}:{PORT}/login"

