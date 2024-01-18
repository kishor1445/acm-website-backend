from typing import AsyncIterable
import pytest
import pytest_asyncio
import httpx
from . import config

ACCESS_TOKEN = None


@pytest_asyncio.fixture()
async def client() -> AsyncIterable[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=config.app, base_url="http://test.server/members"
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
async def test_create_member(
    client: httpx.AsyncClient, password: str, target_status_code: int
) -> None:
    res = await client.post(
        "/",
        json={
            "reg_no": 123456,
            "email": "test-acm-sist@gmail.com",
            "name": "TestName",
            "department": "B.E CSE AI-ML",
            "year": 2,
            "password": password,
            "team": "technical",
            "season": 2,
            "linkedin_tag": "test_username",
            "instagram_tag": "test_username",
        },
        follow_redirects=True,
    )
    assert res.status_code == target_status_code


@pytest.mark.parametrize(
    "email, password, target_status_code",
    [
        ("test@gmail.com", "Test@2024", 401),
        ("test-acm-sist@gmail.com", "Test2024", 401),
        ("test-acm-sist@gmail.com", "Test@2024", 200),
    ],
)
@pytest.mark.asyncio
async def test_login_member(
    client: httpx.AsyncClient, email: str, password: str, target_status_code: int
):
    res = await client.post("/login", data={"username": email, "password": password})
    if res.status_code == 200:
        global ACCESS_TOKEN
        ACCESS_TOKEN = res.json()["access_token"]
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


@pytest.mark.parametrize(
    "team", ["core", "technical", "design", "management", "content", "invalid"]
)
@pytest.mark.asyncio
async def test_member_search_by_team(client: httpx.AsyncClient, team: str):
    res = await client.get(f"/search?team={team}")
    if team != "invalid":
        assert res.status_code == 200
    else:
        assert res.status_code == 422


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_member_update(client: httpx.AsyncClient):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    res = await client.patch("/", json={"new_reg_no": 1}, headers=headers)
    assert res.status_code == 200


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.asyncio
async def test_member_me(client: httpx.AsyncClient):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    res = await client.get("/me", headers=headers)
    assert res.status_code == 200
