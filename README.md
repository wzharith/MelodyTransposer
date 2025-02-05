# Saxophone Music Transcriber

A Streamlit-powered music transcription tool specifically designed for saxophonists, enabling audio-to-sheet music conversion and transposition with advanced music processing capabilities.

## Features

- Audio file upload and processing
- Melody extraction using librosa
- Sheet music generation with music21
- Score transposition for saxophone
- MusicXML output display
- Save and manage transcriptions with PostgreSQL

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Required Python packages (installed via Replit)

## Setup

1. Fork this project on Replit
2. Configure environment variables:
   - `DATABASE_URL`: PostgreSQL database URL
   
3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Upload an audio file (WAV or MP3)
2. Enter the song title and any performance notes
3. The app will:
   - Extract the melody
   - Generate sheet music
   - Suggest optimal keys for saxophone
4. Choose your target key for transposition
5. View and download the scores in MusicXML format
6. Save your transcriptions for later reference

## Development

The project uses:
- Streamlit for the web interface
- librosa for audio processing
- music21 for music notation
- SQLAlchemy with PostgreSQL for data storage

## License

MIT License
