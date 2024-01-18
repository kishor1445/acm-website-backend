from typing import AsyncIterable
import os
import pytest
import pytest_asyncio
import httpx
from . import config

VERIFY_TOKEN = None
PASSWORD_RESET_TOKEN = None
ACCESS_TOKEN = None
USER_ACC_INFO = {
    "reg_no": 123456,
    "email": "test-acm-sist@gmail.com",
    "name": "TestName",
    "department": "CSE AI-ML",
    "university": "Sathyabama University",
    "year": 2,
}


@pytest_asyncio.fixture()
async def client() -> AsyncIterable[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=config.app, base_url="http://test.server/users"
    ) as client:
        yield client


@pytest.mark.parametrize(
    "password, target_status_code",
    [
        ("Test", 400),
        ("Test2024", 400),
        ("Test@", 400),
        ("Test@2024", 201),
        ("Test@2024", 409),
    ],
)
@pytest.mark.asyncio
async def test_create_user(
    client: httpx.AsyncClient, password: str, target_status_code: int
) -> None:
    temp_user_acc_info = USER_ACC_INFO
    temp_user_acc_info["password"] = password
    res = await client.post(
        "/",
        json=temp_user_acc_info,
        follow_redirects=True,
    )
    assert res.status_code == target_status_code


@pytest.mark.asyncio
async def test_login_without_verify(client: httpx.AsyncClient):
    res = await client.post(
        "/login", data={"username": USER_ACC_INFO["email"], "password": "Test@2024"}
    )
    assert res.status_code == 403


@pytest.mark.parametrize(
    "email, target_status_code",
    [("test-acm-sist@gmail.com", 200), ("test-acm-sist@gmail.com", 401)],
)
@pytest.mark.asyncio
async def test_verify_user(
    client: httpx.AsyncClient, email: str, target_status_code: int
):
    res = await client.get(f"/verify?token={VERIFY_TOKEN}&email={email}")
    assert res.status_code == target_status_code


@pytest.mark.parametrize(
    "email, password, target_status_code",
    [
        ("test@gmail.com", "Test@2024", 401),
        (USER_ACC_INFO["email"], "Test2024", 401),
        (USER_ACC_INFO["email"], "Test@2024", 200),
    ],
)
@pytest.mark.asyncio
async def test_login_user(
    client: httpx.AsyncClient, email: str, password: str, target_status_code: int
):
    res = await client.post("/login", data={"username": email, "password": password})
    if res.status_code == 200:
        global ACCESS_TOKEN
        ACCESS_TOKEN = res.json()["access_token"]
    assert res.status_code == target_status_code


@pytest.mark.parametrize(
    "email, target_status_code",
    [
        ("doesNotExist@gmail.com", 200),
        ("test-acm-sist@gmail.com", 200),
        ("test-acm-sist@gmail.com", 403),
    ],
)
@pytest.mark.asyncio
async def test_forgot_password(
    client: httpx.AsyncClient, email: str, target_status_code: int
):
    res = await client.post("/forgot_password", json={"email": email})
    assert res.status_code == target_status_code


@pytest.mark.asyncio
async def test_show_reset_pass_page(client: httpx.AsyncClient):
    res = await client.get(
        f"/reset_password?email={USER_ACC_INFO['email']}&token={PASSWORD_RESET_TOKEN}"
    )
    assert res.status_code == 200


@pytest.mark.parametrize(
    "password, target_status_code",
    [
        ("Test", 400),
        ("Test123", 400),
        ("Test2025", 400),
        ("Test@2025", 403),
        ("Test@2025", 200),
    ],
)
@pytest.mark.asyncio
async def test_reset_password_by_mail(
    client: httpx.AsyncClient, password: str, target_status_code: int
):
    if target_status_code == 403:
        email = "doesNotExist@gmail.com"
    else:
        email = USER_ACC_INFO["email"]
    res = await client.post(
        "/reset_password",
        json={
            "new_password": password,
            "confirm_password": password,
            "reset_token": PASSWORD_RESET_TOKEN,
            "email": email,
        },
    )
    assert res.status_code == target_status_code


@pytest.mark.parametrize(
    "password, target_status_code",
    [
        ("Test", 400),
        ("Test123", 400),
        ("Test2024", 400),
        ("Test@2024", 401),
        ("Test@2024", 200),
    ],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_reset_password_by_auth(
    client: httpx.AsyncClient, password: str, target_status_code: int
):
    if target_status_code == 401:
        headers = {"Authorization": "Bearer AN-INVALID-TOKEN"}
    else:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    res = await client.post(
        "/reset_password",
        headers=headers,
        json={"new_password": password, "confirm_password": password},
    )
    assert res.status_code == target_status_code


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_user_me(client: httpx.AsyncClient):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    res = await client.get("/me", headers=headers)
    assert res.status_code == 200


def test_cleanup():
    """
    Removes the acm-test.db so it won't conflict when we run the tests again
    """
    os.remove("acm-test.db")

# TODO: Complete remaining tests
