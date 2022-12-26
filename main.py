import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials

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
            {"name": "Mathieu van der Poel", "team": "	Alpecin-Deceuninck", "race_won": 8},
            {"name": "Peter Sagan", "team": "TotalEnergies", "race_won": 32}]

# GET endpoint to retrieve a specific item
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"name": "Wout Van Aert", "team": "Jumbo Visma", "race_won": 18}

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