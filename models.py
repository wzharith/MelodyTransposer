from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os

Base = declarative_base()

class Song(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    original_key = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    transcriptions = relationship("Transcription", back_populates="song")

class Transcription(Base):
    __tablename__ = 'transcriptions'
    
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id'))
    target_key = Column(String(10), nullable=False)
    sheet_data = Column(Text, nullable=False)  # Store the music21 score as serialized data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    song = relationship("Song", back_populates="transcriptions")

# Database initialization
def init_db():
    engine = create_engine(os.getenv('DATABASE_URL'))
    Base.metadata.create_all(engine)
