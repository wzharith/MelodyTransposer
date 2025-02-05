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
db = next(get_db())

# Show previous transcriptions
st.sidebar.header("Previous Transcriptions")
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

# File upload and song title
col1, col2 = st.columns([2, 1])
with col1:
    audio_file = st.file_uploader("Upload your audio file", type=['wav', 'mp3'])
with col2:
    song_title = st.text_input("Song Title")
    notes = st.text_area("Performance Notes", height=100)

if audio_file is not None and song_title:
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
        except Exception as e:
            st.error(f"Error loading audio: {str(e)}")
            st.stop()

        with st.spinner("Extracting melody..."):
            try:
                # Extract melody
                notes_data = extract_melody(y, sr)
                st.success(f"Melody extracted: {len(notes_data)} notes found")

                # Create initial score
                score = create_music_score(notes_data)

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

                # Save button
                if st.button("Save Transcription"):
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

                # Display scores
                st.subheader("Original Score")
                try:
                    st.image(score.show(), use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying original score: {str(e)}")

                st.subheader("Transposed Score")
                try:
                    st.image(transposed_score.show(), use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying transposed score: {str(e)}")

            except Exception as e:
                st.error(f"Error processing melody: {str(e)}")
                st.stop()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
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