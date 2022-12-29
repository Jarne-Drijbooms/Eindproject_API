import secrets

import auth
import crud
import schemas
import models
import os
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session


if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"admin@mysite.com"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"swordfish"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


#@app.get("/users/me")
#def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
#    return {"username": credentials.username, "password": credentials.password}

class Item(BaseModel):
    name: str
    team: str
    race_won: int

# GET endpoint to retrieve a list of items
@app.get("/items/")
async def read_items():
    return [{"name": "Wout Van Aert", "team": "Jumbo Visma", "race_won": 18},
            {"name": "Mathieu van der Poel", "team": "Alpecin-Deceuninck", "race_won": 8},
            {"name": "Peter Sagan", "team": "TotalEnergies", "race_won": 32}]

# GET endpoint to retrieve a specific item
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"name": "Wout Van Aert", "team": "Jumbo Visma", "race_won": 18, "item_id": item_id}


#@app.get("/items/2")
#async def read_item(item_id: int):
#    return {"name": "Mathieu van der Poel", "team": "Alpecin-Deceuninck", "race_won": 8}


#@app.get("/items/3")
#async def read_item(item_id: int):
#    return {"name": "Peter Sagan", "team": "TotalEnergies", "race_won": 32}


# POST endpoint to create a new item
@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "team": item.team, "race_won": item.race_won}

# PUT endpoint to update an existing item
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"name": item.name, "team": item.team, "race_won": item.race_won}

# DELETE endpoint to delete an item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"message": "Item deleted"}


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users
