from database import Base
from sqlalchemy import Column, Integer, String

class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    score = Column(Integer)
    status = Column(String)
