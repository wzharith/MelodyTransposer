from music21 import *

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
    # Get current key
    current_key = score.analyze('key')
    
    # Calculate interval for transposition
    interval = interval.Interval(current_key.tonic, key.Key(target_key).tonic)
    
    # Create new score with transposition
    return score.transpose(interval)

def suggest_best_key(score):
    """
    Suggest the best key for saxophone performance
    
    Args:
        score (music21.stream.Score): Musical score
    
    Returns:
        str: Suggested key
    """
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

def get_available_keys():
    """
    Get list of available keys for transposition
    
    Returns:
        list: Available keys
    """
    major_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#',
                  'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
    return major_keys
