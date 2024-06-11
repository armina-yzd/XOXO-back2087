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

class PlayerModel(PlayerBase):
    class Config:
        from_attributes = True



class PlayerUpdate(BaseModel):
    name: str 
    status: str 

def get_db():
    db =  SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind= engine)

@app.post("/player/",response_model=PlayerUpdate)
async def create_player(player: PlayerUpdate, db: db_dependency):
    playerUP = db.query(models.Player).filter_by(name=player.name).first()
    if playerUP is None:
        playerU = models.Player(name=player.name, score=0)
        db.add(playerU)
        db.commit()
        db.refresh(playerU)

    return player

    
    

@app.put("/player/",response_model=PlayerUpdate)
async def updatePlayer( player: PlayerUpdate, db: db_dependency):
    playerUP = db.query(models.Player).filter_by(name=player.name).first()
    if playerUP is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if(player.status == "WIN"):
        playerUP.score +=1
    elif(player.status == "LOSE"):
        playerUP.score -=1

    db.commit()
    db.refresh(playerUP)

    return player



@app.get("/player/", response_model=list[PlayerModel])
async def read_player(db: db_dependency, skip: int = 0, limit: int = 100):
    players = db.query(models.Player).offset(skip).limit(limit).all()
    players.sort(key=operator.attrgetter('score'))
    players.reverse()
    return players[0:10]