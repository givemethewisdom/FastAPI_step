from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth.security import hashed_content


security = HTTPBasic()

# по этой схеме работает/ некоторые другие нет


async def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username is None or credentials.password is None:
        raise HTTPException(401, detail="Incorrect credentials", headers={"WWW-Authenticate": "Basic"})

    if credentials.username not in fake_db:
        raise HTTPException(401, detail="Incorrect credentials", headers={"WWW-Authenticate": "Basic"})

    if not hashed_content.verify(credentials.password, fake_db[credentials.username]):
        raise HTTPException(401, detail="Incorrect credentials", headers={"WWW-Authenticate": "Basic"})

    return credentials.username
