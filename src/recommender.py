from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked for the given user."""
        scored_songs = sorted(
            self.songs,
            key=lambda song: self._score_song_for_user(user, song),
            reverse=True,
        )
        return scored_songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short explanation for why a song matches the user."""
        _, reasons = self._score_song_details(user, song)
        return ", ".join(reasons)

    def _score_song_for_user(self, user: UserProfile, song: Song) -> float:
        """Compute the numeric match score for one song."""
        score, _ = self._score_song_details(user, song)
        return score

    def _score_song_details(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Calculate a song's score and the reasons behind it."""
        score = 0.0
        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            score += 0.75
            reasons.append("genre match (+0.75)")

        if song.mood.lower() == user.favorite_mood.lower():
            score += 0.5
            reasons.append("mood match (+0.5)")

        energy_diff = abs(song.energy - user.target_energy)
        energy_score = (1 - energy_diff) * 2
        score += energy_score
        reasons.append(f"energy similarity (+{energy_score:.2f})")

        if user.likes_acoustic and song.acousticness >= 0.6:
            score += 0.25
            reasons.append("acoustic bonus (+0.25)")
        elif not user.likes_acoustic and song.acousticness <= 0.4:
            score += 0.25
            reasons.append("non-acoustic bonus (+0.25)")

        return score, reasons

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    songs = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Convert numeric fields to proper types
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])

            songs.append(row)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences and list the reasons."""
    score = 0.0
    reasons = []

    if song["genre"].lower() == user_prefs["genre"].lower():
        score += 0.75
        reasons.append("genre match (+0.75)")

    if song["mood"].lower() == user_prefs["mood"].lower():
        score += 0.5
        reasons.append("mood match (+0.5)")

    energy_diff = abs(song["energy"] - user_prefs["energy"])
    energy_score = (1 - energy_diff) * 2
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top k scored songs with explanation strings."""
    scored = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
