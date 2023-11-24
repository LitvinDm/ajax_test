from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from utils import app_username, app_password, get_api_data, get_db_data, combine_data
from models import SessionLocal

app = FastAPI()
security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == app_username and credentials.password == app_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users")
async def users(db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate_user)):

    res_db = get_db_data(db)
    res_api = await get_api_data()
    return combine_data(res_api, res_db)

@app.get("/users/{id}")
async def users(id: int, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate_user)):

    res_db = get_db_data(db, id)
    res_api = await get_api_data(id)

    return combine_data(res_api, res_db)