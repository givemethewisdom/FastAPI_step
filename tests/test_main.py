# tests/test_users.py
import pytest



class TestCreateUser:
    """Тесты для создания пользователя"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Успешное создание пользователя"""
        try:
            user_data = {
                "username": "testuser",
                "info": "some info",
                "password": "securepassword123"
            }

            response = await client.post("/users/create", json=user_data)

            if response.status_code != 200:
                # Попробуйте получить текст ошибки
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
    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, client):
        """Создание пользователя без обязательных полей"""
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

    @pytest.mark.asyncio
    async def test_create_user_empty_fields(self, client):
        """Создание пользователя с пустыми полями"""
        try:
            response = await client.post("/users/create", json={
                "username": "",
                "password": "",
                "info": ""
            })
            assert response.status_code in [422, 400]  # Валидация должна падать

        except Exception as e:
            pytest.fail(f'{e}')

    @pytest.mark.asyncio
    async def test_create_user_password_length(self, client):
        """Проверка минимальной длины пароля"""
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

    @pytest.mark.asyncio
    async def test_create_user_sql_injection_attempt(self, client):
        """Попытка SQL-инъекции в полях"""
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