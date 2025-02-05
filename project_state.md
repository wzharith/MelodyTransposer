# Saxophone Music Transcriber - Current State

## Project Description
A Streamlit-powered music transcription tool specifically designed for saxophonists, enabling audio-to-sheet music conversion and transposition with advanced music processing capabilities.

## Current Implementation Status
- Basic Streamlit interface with file upload ✓
- Audio processing with librosa ✓
- Music transcription with music21 ✓
- Database integration with PostgreSQL ✓
- Score transposition functionality ✓
- MusicXML output display ✓

## Files Structure
```
├── .streamlit/
│   └── config.toml
├── assets/
│   └── app.css
├── utils/
│   ├── audio_processor.py
│   └── music_processor.py
├── database.py
├── init_db.py
├── main.py
└── models.py
```

## File Contents

### .streamlit/config.toml
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FFB84C"
backgroundColor = "#F5F5F5"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
```

### assets/app.css
```css
/* Main styling */
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}

/* Header styling */
.main .block-container h1 {
    color: #2C3E50;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

/* File uploader styling */
.uploadedFile {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
}

/* Spinner styling */
.stSpinner > div {
    border-color: #FFB84C !important;
}

/* Tips section styling */
.markdown-text-container {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-top: 30px;
}

/* Select box styling */
.stSelectbox {
    margin: 20px 0;
}

/* Error message styling */
.stAlert {
    background-color: #ffe6e6;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}

/* Score display styling */
img {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

### utils/audio_processor.py
```python
import librosa
import numpy as np
from music21 import note, stream
import logging

def extract_melody(y, sr):
    """
    Extract melody from audio using librosa

    Args:
        y (np.ndarray): Audio time series
        sr (int): Sampling rate

    Returns:
        list: List of music21 notes
    """
    try:
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # Get the most prominent pitch at each time
        pitches_with_max_magnitude = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Filter out silence
                pitches_with_max_magnitude.append(pitch)

        if not pitches_with_max_magnitude:
            raise ValueError("No pitches detected in the audio")

        # Convert frequencies to MIDI notes
        midi_notes = librosa.hz_to_midi(np.array(pitches_with_max_magnitude))

        # Quantize notes to nearest semitone
        midi_notes = np.round(midi_notes)

        # Convert to music21 notes
        notes = []
        current_note = None
        current_duration = 0

        for midi_pitch in midi_notes:
            if current_note is None:
                current_note = midi_pitch
                current_duration = 1
            elif midi_pitch == current_note:
                current_duration += 1
            else:
                # Create note object
                n = note.Note(int(current_note))
                n.quarterLength = current_duration * 0.25  # Adjust duration
                notes.append(n)
                current_note = midi_pitch
                current_duration = 1

        # Add last note
        if current_note is not None:
            n = note.Note(int(current_note))
            n.quarterLength = current_duration * 0.25
            notes.append(n)

        if not notes:
            raise ValueError("Failed to create notes from the detected pitches")

        return notes

    except Exception as e:
        logging.error(f"Error in extract_melody: {str(e)}")
        raise
```

### utils/music_processor.py
```python
from music21 import *
import logging
import os

# Configure music21 to use basic formats
us = environment.UserSettings()
us['warnings'] = 0
us['directoryScratch'] = '/tmp'

def create_music_score(notes):
    """
    Create a music21 score from notes

    Args:
        notes (list): List of music21 notes

    Returns:
        music21.stream.Score: Musical score
    """
    s = stream.Score()
    p = stream.Part()

    # Add time signature and clef
    p.append(meter.TimeSignature('4/4'))
    p.append(clef.TrebleClef())

    # Add notes to part
    for n in notes:
        p.append(n)

    s.append(p)
    return s

def transpose_score(score, target_key):
    """
    Transpose score to target key

    Args:
        score (music21.stream.Score): Original score
        target_key (str): Target key

    Returns:
        music21.stream.Score: Transposed score
    """
    try:
        # Get current key
        current_key = score.analyze('key')

        # Create key objects
        target_key_obj = key.Key(target_key)

        # Calculate interval between current and target key
        int_interval = interval.Interval(current_key.tonic, target_key_obj.tonic)

        # Create new score with transposition
        return score.transpose(int_interval)
    except Exception as e:
        logging.error(f"Error in transpose_score: {str(e)}")
        raise

def suggest_best_key(score):
    """
    Suggest the best key for saxophone performance

    Args:
        score (music21.stream.Score): Musical score

    Returns:
        str: Suggested key
    """
    try:
        # Common comfortable keys for saxophone
        sax_friendly_keys = ['C', 'G', 'F', 'D', 'Bb', 'A']

        current_key = score.analyze('key')

        # Find closest key with minimal accidentals
        min_accidentals = float('inf')
        best_key = None

        for k in sax_friendly_keys:
            test_key = key.Key(k)
            accidentals = len(test_key.alteredPitches)
            if accidentals < min_accidentals:
                min_accidentals = accidentals
                best_key = k

        return best_key
    except Exception as e:
        logging.error(f"Error in suggest_best_key: {str(e)}")
        raise

def get_available_keys():
    """
    Get list of available keys for transposition

    Returns:
        list: Available keys
    """
    major_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#',
                  'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
    return major_keys
```

### database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Create database engine
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### init_db.py
```python
from models import init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
```

### models.py
```python
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
```

### main.py
[File is too long to include here, but it contains the Streamlit interface implementation with file upload, audio processing, and score display functionality]

## Required Dependencies
```python
music21
numpy
psycopg2-binary
sqlalchemy
streamlit
librosa
```

## Suggested Prompt for Next Chat
```
We're working on a Saxophone Music Transcriber project. The current implementation includes:
- Streamlit web interface
- Audio processing with librosa
- Music transcription with music21
- PostgreSQL database integration
- Score transposition functionality
- MusicXML output display

The app currently allows users to:
1. Upload audio files
2. Extract melodies
3. View and transpose sheet music
4. Save transcriptions to database

Latest implemented feature: Fixed score display issues by switching to MusicXML format output.

Future features to implement:
- MIDI file export
- Chord recognition

Please help continue development from this point.
```
