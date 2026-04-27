from pathlib import Path

from src.recommender import (
    Recommender,
    SocialRecommender,
    Song,
    UserProfile,
    load_social_music_data,
    run_reliability_checks,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_new_user_onboarding_recommendations_use_social_data():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data = load_social_music_data(data_dir)
    recommender = SocialRecommender(data)

    results = recommender.recommend_for_user("u9", k=5)

    assert len(results) == 5
    assert any("cold-start mode" in reason for reason in results[0].reasons)


def test_reliability_checks_pass_for_seed_dataset():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data = load_social_music_data(data_dir)

    report = run_reliability_checks(data)

    assert report["passed"] == report["total"]
