import streamlit as st
import librosa
import numpy as np
from utils.audio_processor import extract_melody
from utils.music_processor import (
    create_music_score,
    transpose_score,
    suggest_best_key,
    get_available_keys
)
from models import Song, Transcription
from database import get_db
from sqlalchemy.orm import Session
import pickle
import io
import logging
import os
from music21 import environment
import base64
from tempfile import NamedTemporaryFile

# Configure music21 to use basic formats
us = environment.UserSettings()
us['warnings'] = 0
us['directoryScratch'] = '/tmp'

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Sax Music Transcriber",
    page_icon="🎷",
    layout="wide"
)

# Custom CSS
with open('assets/app.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🎷 Saxophone Music Transcriber")
st.markdown("""
    Upload your audio file, and we'll help you transcribe and transpose it to the most
    comfortable key for saxophone performance.
""")

# Initialize database session
try:
    db = next(get_db())
except Exception as e:
    st.error(f"Database connection error: {str(e)}")
    st.stop()

# Show previous transcriptions
st.sidebar.header("Previous Transcriptions")
try:
    previous_songs = db.query(Song).order_by(Song.created_at.desc()).all()
    if previous_songs:
        selected_song = st.sidebar.selectbox(
            "Load previous transcription:",
            options=previous_songs,
            format_func=lambda x: x.title
        )
        if selected_song:
            st.sidebar.write(f"Original Key: {selected_song.original_key}")
            st.sidebar.write(f"Notes: {selected_song.notes}")
except Exception as e:
    st.sidebar.error(f"Error loading previous transcriptions: {str(e)}")

# File upload and song title
col1, col2 = st.columns([2, 1])
with col1:
    audio_file = st.file_uploader("Upload your audio file", type=['wav', 'mp3'])
with col2:
    song_title = st.text_input("Song Title")
    notes = st.text_area("Performance Notes", height=100)

if audio_file is not None:
    if not song_title:
        st.warning("Please enter a song title before proceeding.")
        st.stop()

    try:
        # Load and process audio
        st.audio(audio_file)

        # Debug info
        st.info(f"Processing file: {audio_file.name}")

        # Convert uploaded file to bytes
        audio_bytes = audio_file.read()
        audio_file.seek(0)  # Reset file pointer

        # Load audio using librosa
        try:
            y, sr = librosa.load(io.BytesIO(audio_bytes))
            st.success(f"Audio loaded successfully: {sr}Hz sampling rate, {len(y)} samples")
            if len(y) == 0:
                st.error("The audio file appears to be empty.")
                st.stop()
        except Exception as e:
            st.error(f"Error loading audio: {str(e)}")
            logging.error(f"Audio loading error: {str(e)}")
            st.stop()

        with st.spinner("Extracting melody..."):
            try:
                # Extract melody
                notes_data = extract_melody(y, sr)
                if not notes_data:
                    st.error("No melody could be extracted from the audio.")
                    st.stop()
                st.success(f"Melody extracted: {len(notes_data)} notes found")

                # Create initial score
                score = create_music_score(notes_data)
                if not score:
                    st.error("Failed to create music score from the extracted notes.")
                    st.stop()

                # Display original key
                original_key = score.analyze('key')
                st.write(f"Original Key: {original_key}")

                # Key suggestion
                suggested_key = suggest_best_key(score)
                st.write(f"Suggested Key for Saxophone: {suggested_key}")

                # Transposition options
                col1, col2 = st.columns(2)

                with col1:
                    available_keys = get_available_keys()
                    target_key = st.selectbox(
                        "Select target key:",
                        available_keys,
                        index=available_keys.index(str(suggested_key))
                    )

                with col2:
                    st.write("Common saxophone keys:")
                    st.write("- Concert Eb → Alto Sax C")
                    st.write("- Concert Bb → Alto Sax G")

                # Transpose score
                transposed_score = transpose_score(score, target_key)
                if not transposed_score:
                    st.error("Failed to transpose the score.")
                    st.stop()

                # Cache for rendered scores
                if 'score_cache' not in st.session_state:
                    st.session_state.score_cache = {}

                def render_score(score, cache_key):
                    """Render a music21 score to PNG and return as base64 string"""
                    if cache_key in st.session_state.score_cache:
                        return st.session_state.score_cache[cache_key]

                    try:
                        # Create a temporary file for the PNG
                        with NamedTemporaryFile(suffix='.png') as tmp:
                            # Export score to PNG
                            score.write('musicxml.png', fp=tmp.name)

                            # Read the PNG data
                            with open(tmp.name, 'rb') as f:
                                img_data = f.read()

                            # Convert to base64
                            img_b64 = base64.b64encode(img_data).decode()
                            html = f'<img src="data:image/png;base64,{img_b64}" style="max-width: 100%;">'

                            # Cache the result
                            st.session_state.score_cache[cache_key] = html
                            return html
                    except Exception as e:
                        st.error(f"Error rendering score: {str(e)}")
                        return None


                # Save button
                if st.button("Save Transcription"):
                    try:
                        # Create new song entry
                        song = Song(
                            title=song_title,
                            original_key=str(original_key),
                            notes=notes
                        )
                        db.add(song)
                        db.flush()

                        # Save original transcription
                        original_trans = Transcription(
                            song_id=song.id,
                            target_key=str(original_key),
                            sheet_data=pickle.dumps(score)
                        )
                        db.add(original_trans)

                        # Save transposed version
                        transposed_trans = Transcription(
                            song_id=song.id,
                            target_key=target_key,
                            sheet_data=pickle.dumps(transposed_score)
                        )
                        db.add(transposed_trans)

                        db.commit()
                        st.success("Transcription saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving transcription: {str(e)}")
                        logging.error(f"Database save error: {str(e)}")
                        db.rollback()

                # Display scores
                st.subheader("Original Score")
                try:
                    original_html = render_score(score, f"original_{song_title}")
                    if original_html:
                        st.markdown(original_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying original score: {str(e)}")
                    logging.error(f"Score display error: {str(e)}")

                st.subheader("Transposed Score")
                try:
                    transposed_html = render_score(transposed_score, f"transposed_{song_title}_{target_key}")
                    if transposed_html:
                        st.markdown(transposed_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying transposed score: {str(e)}")
                    logging.error(f"Transposed score display error: {str(e)}")

            except Exception as e:
                st.error(f"Error processing melody: {str(e)}")
                logging.error(f"Melody processing error: {str(e)}")
                st.stop()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logging.error(f"General error: {str(e)}")
        st.write("Please try uploading a different audio file.")

# Add helpful information
st.markdown("""
    ### Tips:
    - Upload clear audio recordings for better transcription
    - Common saxophone transpositions are already suggested
    - The tool will suggest keys with fewer accidentals
    - You can manually select any key for transposition
    - Save your transcriptions to access them later
""")