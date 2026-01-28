from httpx import AsyncClient, ASGITransport

from app.main import app


async def test_get_users():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        response = await ac.get("/users/get_all")
    assert response.status_code == 200