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

# File upload
audio_file = st.file_uploader("Upload your audio file", type=['wav', 'mp3'])

if audio_file is not None:
    try:
        # Load and process audio
        st.audio(audio_file)
        
        y, sr = librosa.load(audio_file)
        
        with st.spinner("Extracting melody..."):
            # Extract melody
            notes = extract_melody(y, sr)
            
            # Create initial score
            score = create_music_score(notes)
            
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
            
            # Display scores
            st.subheader("Original Score")
            st.image(score.show(), use_column_width=True)
            
            st.subheader("Transposed Score")
            st.image(transposed_score.show(), use_column_width=True)
            
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
""")
