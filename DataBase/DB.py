from app.models.models import UserBaseFields

REFRESH_TOKEN_DB = {

}

# Фиктивные данные пользователей (в реальном проекте тут будет БД)
USERS_DATA = [
    {
        "username": "admin",
        "password": "adminpass",  # В продакшене пароли должны быть хешированы!
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False
    },
    {
        "username": "da",
        "password": "da",  # В продакшене пароли должны быть хешированы!
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False
    },
    {
        "username": "user",
        "password": "userpass",
        "roles": ["user"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False
    },
    {
        "username": "guest",
        "password": "guestpass",
        "roles": ["guest"],
        "full_name": "Guest User",
        "email": "guest@example.com",
        "disabled": False
    }
]

# Список для редактирования с разными правами(удалить когда начну работать с ДБ)
USERS_FOR_DELETE = {
    "user1": {
        "username": "user1",
        "password": "<PASSWORD>",
        "roles": ["user"]
    }
}


def get_user(username: str) -> UserBaseFields | None:
    """Получаем пользователя по имени (без пароля)"""
    for user_data in USERS_DATA:
        if user_data["username"] == username:
            if not user_data["disabled"]:
                return UserBaseFields(**{k: v for k, v in user_data.items() if k != "password"})
    return None
