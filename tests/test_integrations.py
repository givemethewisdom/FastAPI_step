# tests/test_users.py
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.models import UserReturn


"""class TestCreateUser:
    Тесты для создания пользователя

    async def test_create_user_success(self, client):  # client form conftest
        Успешное создание пользователя
        try:
            user_data = {
                "username": "testuser",
                "info": "some info",
                "password": "securepassword123"
            }

            response = await client.post("/users/create", json=user_data)

            if response.status_code != 200:
                # Пробую получить текст ошибки
                try:
                    error_data = response.json()
                except Exception as e:
                    pytest.fail(f'{e}')

            assert response.status_code == 200, f"Ожидался 200, получили {response.status_code}"

            data = response.json()
            assert data["username"] == user_data["username"]
            assert data["info"] == user_data["info"]
            assert "id" in data
            assert "password" not in data

        except Exception as e:
            pytest.fail(f'{e}')

    async def test_create_user_missing_fields(self, client):
        Создание пользователя без обязательных полей
        try:
            # Без username
            response = await client.post("/users/create", json={
                "password": "password123",
                "info": "Без username"
            })
            assert response.status_code == 422

            # Без password
            response = await client.post("/users/create", json={
                "username": "testuser",
                "info": "Без пароля"
            })
            assert response.status_code == 422

        except Exception as e:
            pytest.fail(f'{e}')

    async def test_create_user_empty_fields(self, client):
        Создание пользователя с пустыми полями
        try:
            response = await client.post("/users/create", json={
                "username": "",
                "password": "",
                "info": ""
            })
            assert response.status_code in [422, 400]  # Валидация должна падать

        except Exception as e:
            pytest.fail(f'{e}')

    async def test_create_user_password_length(self, client):
        Проверка минимальной длины пароля
        try:
            # Слишком короткий пароль
            response = await client.post("/users/create", json={
                "username": "shortpassuser",
                "password": "",  # для отладки пароль от 1 до 128 class UserCreate(UserBase)
                "info": "Тест короткого пароля"
            })

            # Это может быть либо 422 (валидация Pydantic), либо 400
            assert response.status_code in [422, 400]

        except Exception as e:
            pytest.fail(f'{e}')

    async def test_create_user_sql_injection_attempt(self, client):
        Попытка SQL-инъекции в полях
        try:
            user_data = {
                "username": "test'; DROP TABLE users; --",
                "password": "password123",
                "info": "Тест на SQL-инъекцию"
            }

            response = await client.post("/users/create", json=user_data)

            # Должен создаться пользователь с таким username (SQLAlchemy защищает от инъекций)
            # Но можно проверить, что система не падает
            assert response.status_code in [200, 422, 400]

        except Exception as e:
            pytest.fail(f'{e}')


class TestGetUser:

    async def test_get_users_zero_users(self, client):
        get_response = await client.get("/users/get_all")
        assert get_response.status_code == 200

        data = get_response.json()
        assert isinstance(data, list)

    async def test_get_users(self, client):
        # create user lrdy tested before

        user_data = [
            {"username": "testuser", "info": "some info", "password": "securepassword123"},
            {"username": "test new user", "info": "more some info", "password": "damskiyugodnik217"}
        ]
        id_list = []
        for user in user_data:
            response = await client.post("/users/create", json=user)
            assert response.status_code == 200
            id_list.append(response.json()['id'])

        get_response = await client.get("/users/get_all")
        data = get_response.json()
        assert isinstance(data, list)
        assert len(data) == len(user_data)

        for i, user in enumerate(data):
            try:
                UserReturn(**user)

                assert user['id'] in id_list
                expected_user = user_data[i]
                assert expected_user['username'] == user['username']
                assert expected_user['info'] == user['info']
                # рекомендуется проверять пароль но user валидируется под модель без пароля
                # и я не знаю зачем это делать
                assert 'password' not in user
            except Exception as e:
                pytest.fail(f'user have no valid structure: {e}')

    async def test_get_user_by_id(self, client):
        create_resp = await client.post("/users/create", json={
            "username": "john",
            "password": "pass",
            "info": "info"
        })

        user_id = create_resp.json()["id"]

        get_resp = await client.get(f"/users/{user_id}")

        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == user_id"""
