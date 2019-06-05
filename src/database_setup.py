import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Clickbait(Base):
    __tablename__ = 'clickbait'
    # __table_args__ = {'autoload': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    clickbaitiness = Column(Float, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'clickbaitiness': self.clickbaitiness
        }

class Stance(Base):
    __tablename__ = 'stance'
    # __table_args__ = {'autoload': True}

    id      = Column(Integer, primary_key=True)
    title   = Column(String(500), nullable=False)
    content = Column(String, nullable=False)
    stance  = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'stance': self.stance
        }


engine = create_engine('sqlite:///cnn.db')


Base.metadata.create_all(engine)
