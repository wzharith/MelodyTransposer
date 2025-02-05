import librosa
import numpy as np
from music21 import note, stream

def extract_melody(y, sr):
    """
    Extract melody from audio using librosa
    
    Args:
        y (np.ndarray): Audio time series
        sr (int): Sampling rate
    
    Returns:
        list: List of music21 notes
    """
    # Extract pitch
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Get the most prominent pitch at each time
    pitches_with_max_magnitude = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:  # Filter out silence
            pitches_with_max_magnitude.append(pitch)
    
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
    
    return notes
