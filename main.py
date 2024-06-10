import operator
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated,List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from fastapi.encoders import jsonable_encoder
import models
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = {
    'http://localhost:3000',
}

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=['*'],
    allow_headers=['*']
)

class PlayerBase(BaseModel):
    name: str
    score: int
    status: str

class PlayerModel(PlayerBase):
    class Config:
        from_attributes = True

class playerUpdate(BaseModel):
    score: int | None = None
    status: str | None = None

def get_db():
    db =  SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind= engine)

@app.post("/player/",response_model=PlayerModel)
async def create_player(player: PlayerBase, db: db_dependency):
    playerUP = db.query(models.Player).filter_by(name=player.name).first()
    if playerUP is None:
        player.status="NONE"
        player.score = 0
        db_player =  models.Player(**player.dict())
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
        return db_player
    

    return playerUP

    
    
@app.put("/player/{playerName}", response_model=PlayerModel)
async def updatePlayer(playerName: str, player: PlayerBase, db: db_dependency):
    playerUP = db.query(models.Player).filter_by(name=playerName).first()
    if playerUP is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if(player.status == "WIN"):
        player.score +=1
    elif(player.status == "LOSE"):
        player.score -=1

    playerUP.score = player.score
    playerUP.status = "NONE"
    db.commit()
    db.refresh(playerUP)
    return playerUP



@app.get("/player/", response_model=list[PlayerModel])
async def read_player(db: db_dependency, skip: int = 0, limit: int = 100):
    players = db.query(models.Player).offset(skip).limit(limit).all()
    players.sort(key=operator.attrgetter('score'))
    players.reverse()
    return players[0:10]