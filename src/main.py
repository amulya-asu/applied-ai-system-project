"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
    songs = load_songs(str(data_path))
    print(f"Loaded songs: {len(songs)}")
    user_profiles = {
        "Dance on Beat": {"genre": "edm", "mood": "energetic", "energy": 0.9},
        "Silent Getaway": {"genre": "ambient", "mood": "chill", "energy": 0.3},
        "Midnight Steel": {"genre": "metal", "mood": "intense", "energy": 0.95},
    }

    for profile_name, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\n=== {profile_name} ===\n")
        for index, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec
            reasons = explanation.split("; ")

            print(f"[{index}] {song['title']}")
            print(f"    Score  : {score:.2f}")
            print("    Reasons:")
            for reason in reasons:
                print(f"    - {reason}")
            print()


if __name__ == "__main__":
    main()
