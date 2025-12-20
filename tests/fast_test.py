SOME_RESOURSE = {
    "user1": {
        "username": "user1",
        "password": "<PASSWORD>",
        "roles": ["user"]
    }
}

print(SOME_RESOURSE)
del SOME_RESOURSE["user1"]
print(SOME_RESOURSE)