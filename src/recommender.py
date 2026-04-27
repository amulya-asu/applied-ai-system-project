from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import csv
import logging


logger = logging.getLogger(__name__)


@dataclass
class Song:
    """
    Backward-compatible song model used by the original starter tests.
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
    Backward-compatible user preference model used by starter tests.
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    Original song recommender kept for the starter tests.
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = sorted(
            self.songs,
            key=lambda song: self._score_song_for_user(user, song),
            reverse=True,
        )
        return scored_songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score_song_details(user, song)
        return ", ".join(reasons)

    def _score_song_for_user(self, user: UserProfile, song: Song) -> float:
        score, _ = self._score_song_details(user, song)
        return score

    def _score_song_details(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        score = 0.0
        reasons: List[str] = []

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


@dataclass
class SocialUser:
    user_id: str
    name: str
    preferred_genres: List[str]
    preferred_moods: List[str]
    energy_preference: float
    tempo_preference: float
    valence_preference: float
    invited_by: Optional[str]
    onboarding_status: str


@dataclass
class FriendRecommendation:
    recommendation_id: str
    from_user_id: str
    to_user_id: str
    song_id: str
    anonymous: bool
    message: str
    context_tag: str
    listened: bool


@dataclass
class ListeningEvent:
    user_id: str
    song_id: str
    play_count: int
    liked: bool
    source: str


@dataclass
class RecommendationResult:
    song_id: str
    title: str
    artist: str
    score: float
    confidence: float
    reasons: List[str]
    source_breakdown: Dict[str, float]


@dataclass
class SocialMusicData:
    songs: Dict[str, Dict]
    users: Dict[str, SocialUser]
    friendships: Dict[str, set]
    recommendations: List[FriendRecommendation]
    listening_history: List[ListeningEvent]


def load_songs(csv_path: str) -> List[Dict]:
    """
    Backward-compatible loader for the original starter app.
    """

    songs: List[Dict] = []
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            row["id"] = row.get("song_id", row.get("id"))
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row.get("danceability", 0.5))
            row["acousticness"] = float(row.get("acousticness", 0.5))
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    target_genre = user_prefs.get("genre")
    target_mood = user_prefs.get("mood")
    target_energy = user_prefs.get("energy", 0.5)

    if target_genre and song["genre"].lower() == target_genre.lower():
        score += 0.75
        reasons.append("genre match (+0.75)")

    if target_mood and song["mood"].lower() == target_mood.lower():
        score += 0.5
        reasons.append("mood match (+0.5)")

    energy_diff = abs(float(song["energy"]) - float(target_energy))
    energy_score = (1 - energy_diff) * 2
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


def load_social_music_data(data_dir: str | Path) -> SocialMusicData:
    data_path = Path(data_dir)
    return SocialMusicData(
        songs=_load_song_catalog(data_path / "songs.csv"),
        users=_load_users(data_path / "users.csv"),
        friendships=_load_friendships(data_path / "friendships.csv"),
        recommendations=_load_recommendations(data_path / "recommendations.csv"),
        listening_history=_load_listening_history(data_path / "listening_history.csv"),
    )


def _load_song_catalog(csv_path: Path) -> Dict[str, Dict]:
    songs: Dict[str, Dict] = {}
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            songs[row["song_id"]] = {
                "song_id": row["song_id"],
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "duration_sec": int(row["duration_sec"]),
            }
    return songs


def _load_users(csv_path: Path) -> Dict[str, SocialUser]:
    users: Dict[str, SocialUser] = {}
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            users[row["user_id"]] = SocialUser(
                user_id=row["user_id"],
                name=row["name"],
                preferred_genres=row["preferred_genres"].split("|"),
                preferred_moods=row["preferred_moods"].split("|"),
                energy_preference=float(row["energy_preference"]),
                tempo_preference=float(row["tempo_preference"]),
                valence_preference=float(row["valence_preference"]),
                invited_by=row["invited_by"] or None,
                onboarding_status=row["onboarding_status"],
            )
    return users


def _load_friendships(csv_path: Path) -> Dict[str, set]:
    friendships: Dict[str, set] = defaultdict(set)
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            friendships[row["user_id"]].add(row["friend_id"])
    return friendships


def _load_recommendations(csv_path: Path) -> List[FriendRecommendation]:
    recommendations: List[FriendRecommendation] = []
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            recommendations.append(
                FriendRecommendation(
                    recommendation_id=row["recommendation_id"],
                    from_user_id=row["from_user_id"],
                    to_user_id=row["to_user_id"],
                    song_id=row["song_id"],
                    anonymous=row["anonymous"].lower() == "true",
                    message=row["message"],
                    context_tag=row["context_tag"],
                    listened=row["listened"].lower() == "true",
                )
            )
    return recommendations


def _load_listening_history(csv_path: Path) -> List[ListeningEvent]:
    events: List[ListeningEvent] = []
    with open(csv_path, mode="r", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            events.append(
                ListeningEvent(
                    user_id=row["user_id"],
                    song_id=row["song_id"],
                    play_count=int(row["play_count"]),
                    liked=row["liked"].lower() == "true",
                    source=row["source"],
                )
            )
    return events


class SocialRecommender:
    def __init__(self, data: SocialMusicData):
        self.data = data

    def recommend_for_user(self, user_id: str, k: int = 5) -> List[RecommendationResult]:
        user = self.data.users[user_id]
        history = [event for event in self.data.listening_history if event.user_id == user_id]
        cold_start = len(history) < 3 or user.onboarding_status == "new"

        liked_song_ids = {event.song_id for event in history if event.liked}
        candidate_song_ids = set(self.data.songs) - liked_song_ids
        if not candidate_song_ids:
            candidate_song_ids = set(self.data.songs)

        scored_results: List[RecommendationResult] = []
        for song_id in candidate_song_ids:
            song = self.data.songs[song_id]
            score, reasons, breakdown = self._score_song(user_id, song_id, cold_start)
            confidence = min(0.99, round(0.45 + (score / 5.0), 2))
            scored_results.append(
                RecommendationResult(
                    song_id=song_id,
                    title=song["title"],
                    artist=song["artist"],
                    score=round(score, 3),
                    confidence=confidence,
                    reasons=reasons,
                    source_breakdown=breakdown,
                )
            )

        scored_results.sort(key=lambda result: result.score, reverse=True)
        return scored_results[:k]

    def _score_song(self, user_id: str, song_id: str, cold_start: bool) -> Tuple[float, List[str], Dict[str, float]]:
        user = self.data.users[user_id]
        song = self.data.songs[song_id]
        reasons: List[str] = []

        personal_score = self._personal_match_score(user, song, reasons)
        social_score = self._social_influence_score(user_id, song_id, reasons)

        if cold_start:
            personal_weight = 0.45
            social_weight = 0.55
            reasons.append("cold-start mode used friend network because the user has limited history")
        else:
            personal_weight = 0.7
            social_weight = 0.3

        total_score = (personal_score * personal_weight) + (social_score * social_weight)
        breakdown = {
            "personal_score": round(personal_score, 3),
            "social_score": round(social_score, 3),
            "personal_weight": personal_weight,
            "social_weight": social_weight,
        }
        return total_score, reasons, breakdown

    def _personal_match_score(self, user: SocialUser, song: Dict, reasons: List[str]) -> float:
        score = 0.0
        if song["genre"] in user.preferred_genres:
            score += 1.2
            reasons.append(f"genre matched {song['genre']}")
        if song["mood"] in user.preferred_moods:
            score += 0.8
            reasons.append(f"mood matched {song['mood']}")

        energy_score = 1 - abs(song["energy"] - user.energy_preference)
        tempo_score = 1 - min(abs(song["tempo_bpm"] - user.tempo_preference) / 80.0, 1.0)
        valence_score = 1 - abs(song["valence"] - user.valence_preference)
        score += (energy_score * 1.0) + (tempo_score * 0.6) + (valence_score * 0.6)

        if energy_score > 0.85:
            reasons.append("energy level closely matched")
        if tempo_score > 0.8:
            reasons.append("tempo was close to the user's preference")

        return score

    def _social_influence_score(self, user_id: str, song_id: str, reasons: List[str]) -> float:
        score = 0.0
        friends = self.data.friendships.get(user_id, set())
        if not friends:
            return score

        relevant_recommendations = [
            rec
            for rec in self.data.recommendations
            if rec.to_user_id == user_id and rec.song_id == song_id and rec.from_user_id in friends
        ]
        if relevant_recommendations:
            score += 1.0
            transparent_count = sum(1 for rec in relevant_recommendations if not rec.anonymous)
            if transparent_count:
                score += 0.2 * transparent_count
                reasons.append("song was explicitly recommended by a friend")
            anonymous_count = len(relevant_recommendations) - transparent_count
            if anonymous_count:
                score += 0.1 * anonymous_count
                reasons.append("song also appeared in anonymous friend recommendations")

        friend_like_count = 0
        strongest_friend: Optional[str] = None
        strongest_similarity = 0.0
        for friend_id in friends:
            if self._friend_likes_song(friend_id, song_id):
                friend_like_count += 1
                similarity = self._friend_similarity(user_id, friend_id)
                score += 0.35 + (0.35 * similarity)
                if similarity > strongest_similarity:
                    strongest_similarity = similarity
                    strongest_friend = friend_id

        if friend_like_count:
            reasons.append(f"{friend_like_count} connected friend(s) already liked this song")
        if strongest_friend:
            friend_name = self.data.users[strongest_friend].name
            reasons.append(f"{friend_name} has one of the closest taste profiles in the network")

        return score

    def _friend_likes_song(self, friend_id: str, song_id: str) -> bool:
        for event in self.data.listening_history:
            if event.user_id == friend_id and event.song_id == song_id and event.liked:
                return True
        return False

    def _friend_similarity(self, user_id: str, friend_id: str) -> float:
        user = self.data.users[user_id]
        friend = self.data.users[friend_id]

        genre_overlap = len(set(user.preferred_genres) & set(friend.preferred_genres))
        mood_overlap = len(set(user.preferred_moods) & set(friend.preferred_moods))
        energy_gap = abs(user.energy_preference - friend.energy_preference)
        tempo_gap = min(abs(user.tempo_preference - friend.tempo_preference) / 80.0, 1.0)

        raw_score = (genre_overlap * 0.35) + (mood_overlap * 0.25) + ((1 - energy_gap) * 0.25) + ((1 - tempo_gap) * 0.15)
        return min(raw_score / 1.35, 1.0)


def summarize_user_analytics(data: SocialMusicData, user_id: str) -> Dict[str, object]:
    sent_recommendations = [rec for rec in data.recommendations if rec.from_user_id == user_id]
    successful = [rec for rec in sent_recommendations if rec.listened]
    context_counter = Counter(rec.context_tag for rec in successful)

    return {
        "sent_count": len(sent_recommendations),
        "successful_count": len(successful),
        "success_rate": round((len(successful) / len(sent_recommendations)), 2) if sent_recommendations else 0.0,
        "best_context": context_counter.most_common(1)[0][0] if context_counter else None,
    }


def run_reliability_checks(data: SocialMusicData) -> Dict[str, object]:
    recommender = SocialRecommender(data)
    checks: List[Tuple[str, bool]] = []

    zara_top = recommender.recommend_for_user("u9", k=3)
    checks.append(("new user receives onboarding recommendations", len(zara_top) == 3))

    ava_top = recommender.recommend_for_user("u1", k=5)
    checks.append(
        (
            "established user gets at least one preferred genre recommendation",
            any(data.songs[result.song_id]["genre"] in data.users["u1"].preferred_genres for result in ava_top),
        )
    )

    checks.append(
        (
            "friendships exist for every invited user",
            all(
                (user.invited_by is None) or bool(data.friendships.get(user.user_id))
                for user in data.users.values()
            ),
        )
    )

    checks.append(
        (
            "recommendation rows reference valid songs",
            all(rec.song_id in data.songs for rec in data.recommendations),
        )
    )

    passed = sum(1 for _, ok in checks if ok)
    return {
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }


def format_recommendation(result: RecommendationResult) -> str:
    reasons = "; ".join(result.reasons[:4])
    return (
        f"{result.title} by {result.artist} | score={result.score:.2f} | "
        f"confidence={result.confidence:.2f} | {reasons}"
    )


def default_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def build_demo_report(user_id: str, data: SocialMusicData, recommendations: Sequence[RecommendationResult]) -> str:
    user = data.users[user_id]
    lines = [
        f"Profile: {user.name} ({user.user_id})",
        f"Status : {user.onboarding_status}",
        f"Genres : {', '.join(user.preferred_genres)}",
        f"Moods  : {', '.join(user.preferred_moods)}",
        "",
        "Top Recommendations:",
    ]
    for index, result in enumerate(recommendations, start=1):
        lines.append(f"{index}. {format_recommendation(result)}")
    return "\n".join(lines)


def iter_user_history(events: Iterable[ListeningEvent], user_id: str) -> Iterable[ListeningEvent]:
    return (event for event in events if event.user_id == user_id)
