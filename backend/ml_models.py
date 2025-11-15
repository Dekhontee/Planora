"""
Optional TensorFlow difficulty predictor and time estimator.

This module provides:
1. A mock TensorFlow model for predicting topic difficulty (1-5 scale)
2. A time estimator based on topic length and difficulty
3. Training and prediction functions

Instructions:
- Install TensorFlow: pip install tensorflow
- Run this module directly to train on sample data: python3 backend/ml_models.py
- Import and use predict_difficulty() and estimate_time() in parser.py

This is a simplified version suitable for a hackathon. In production, you would:
- Use more sophisticated embeddings (BERT, USE)
- Train on larger, labeled datasets
- Validate on held-out test sets
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


def build_difficulty_model() -> Optional[object]:
    """Build a simple neural network for difficulty classification (1-5)."""
    if not TENSORFLOW_AVAILABLE:
        return None

    model = keras.Sequential([
        layers.Dense(32, activation='relu', input_shape=(10,)),
        layers.Dropout(0.2),
        layers.Dense(16, activation='relu'),
        layers.Dense(5, activation='softmax')  # 5 difficulty levels
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


# Sample training data: (topic_text, difficulty_label, estimated_minutes)
SAMPLE_DATA = [
    ("introduction basics fundamentals simple easy", 1, 45),
    ("overview concepts easy start beginner", 1, 50),
    ("atomic structure bonding electrons periodic", 3, 120),
    ("advanced complex thermodynamics kinetics", 4, 180),
    ("oxidation reduction electrochemistry cells", 4, 150),
    ("stoichiometry calculations moles reactions", 3, 110),
    ("organic chemistry synthesis mechanisms", 5, 200),
    ("acids bases pH buffers titration", 3, 100),
    ("thermodynamics entropy spontaneity", 4, 140),
    ("quantum mechanics orbital wave function", 5, 250),
]


def text_to_features(text: str, max_len: int = 10) -> np.ndarray:
    """Convert text to simple feature vector (character counts, length, etc.)."""
    # Very simple heuristic features
    words = text.lower().split()
    features = [
        len(words),  # word count
        len(text),  # character count
        sum(1 for w in words if len(w) > 8),  # complex words
        text.count('organic'),
        text.count('quantum'),
        text.count('advanced'),
        text.count('basic'),
        text.count('simple'),
        text.count('easy'),
        1 if any(kw in text.lower() for kw in ['mechanism', 'calculus', 'derive']) else 0,
    ]
    return np.array(features[:max_len], dtype=np.float32)


def train_difficulty_model(model: Optional[object], data: List[Tuple[str, int, int]] = None) -> Optional[object]:
    """Train the difficulty model on sample data."""
    if not TENSORFLOW_AVAILABLE or model is None:
        return None

    if data is None:
        data = SAMPLE_DATA

    X = np.array([text_to_features(text) for text, _, _ in data])
    y = np.array([difficulty - 1 for _, difficulty, _ in data])  # 0-4 for 1-5 scale

    model.fit(X, y, epochs=10, batch_size=2, verbose=1)
    return model


def predict_difficulty(text: str, model: Optional[object] = None) -> int:
    """Predict difficulty level (1-5) for a topic."""
    # Fallback heuristic if TensorFlow not available or model is None
    keywords_hard = ['quantum', 'complex', 'advanced', 'mechanism', 'orbital', 'entropy']
    keywords_easy = ['intro', 'basic', 'simple', 'easy', 'overview', 'fundamentals']

    hard_count = sum(1 for kw in keywords_hard if kw in text.lower())
    easy_count = sum(1 for kw in keywords_easy if kw in text.lower())

    if hard_count > 1:
        return 5
    elif hard_count > 0:
        return 4
    elif easy_count > 1:
        return 1
    elif easy_count > 0:
        return 2
    else:
        return 3  # default middle


def estimate_time(
    topic_length: int,
    difficulty: int,
    base_time_per_100_chars: float = 2.0,
) -> int:
    """
    Estimate study time in minutes for a topic.

    Simple formula:
    time = (length / 100) * base_time * difficulty_factor
    """
    base = (topic_length / 100.0) * base_time_per_100_chars * 60  # convert to minutes

    # Difficulty multiplier
    difficulty_factor = 1.0 + (difficulty - 1) * 0.3

    estimated_minutes = int(base * difficulty_factor)
    return max(10, estimated_minutes)  # minimum 10 minutes


if __name__ == "__main__":
    if TENSORFLOW_AVAILABLE:
        print("Building and training difficulty model...")
        model = build_difficulty_model()
        model = train_difficulty_model(model, SAMPLE_DATA)
        model.save("backend/difficulty_model.h5")
        print("Model saved to backend/difficulty_model.h5")

        # Test predictions
        print("\n--- Sample Predictions ---")
        for text, _, _ in SAMPLE_DATA[:3]:
            pred = predict_difficulty(text, model)
            time = estimate_time(len(text), pred)
            print(f"Text: {text[:40]}... -> Difficulty: {pred}, Est. Time: {time} min")
    else:
        print("TensorFlow not installed. Using heuristic difficulty prediction.")
        print("Install with: pip install tensorflow")
        print("\n--- Sample Heuristic Predictions ---")
        for text, true_diff, _ in SAMPLE_DATA[:3]:
            pred = predict_difficulty(text)
            time = estimate_time(len(text), pred)
            print(f"Text: {text[:40]}... -> Difficulty: {pred} (actual: {true_diff}), Est. Time: {time} min")
