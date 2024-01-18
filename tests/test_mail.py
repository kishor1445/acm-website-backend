from typing import AsyncIterable
import pytest
import pytest_asyncio
import httpx
from . import config


@pytest_asyncio.fixture()
async def client() -> AsyncIterable[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=config.app, base_url="http://test.server"
    ) as client:
        yield client


@pytest.mark.parametrize(
    "email, target_status_code",
    [("test@test.com", 201), ("test@test.com", 409), ("testtest.com", 422)],
)
@pytest.mark.asyncio
async def test_subscribe(
    client: httpx.AsyncClient, email: str, target_status_code: int
) -> None:
    res = await client.get(f"/mail/subscribe?email={email}")
    assert res.status_code == target_status_code


@pytest.mark.parametrize(
    "email, target_status_code", [("test@test.com", 204), ("test@test.com", 404)]
)
@pytest.mark.asyncio
async def test_unsubscribe(
    client: httpx.AsyncClient, email: str, target_status_code: int
):
    res = await client.get(f"/mail/unsubscribe?email={email}")
    assert res.status_code == target_status_code
