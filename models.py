from database import Base
from sqlalchemy import Column, Integer, String

class Player(Base):
    __tablename__ = 'player'

    name = Column(String, primary_key=True )
    score = Column(Integer)
