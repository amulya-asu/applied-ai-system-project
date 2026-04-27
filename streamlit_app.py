from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import streamlit as st

from src.recommender import (
    SocialRecommender,
    SocialUser,
    iter_user_history,
    load_social_music_data,
    run_reliability_checks,
    summarize_user_analytics,
)


DATA_DIR = Path(__file__).resolve().parent / "data"

st.set_page_config(
    page_title="Social Music Recommender",
    page_icon="🎵",
    layout="wide",
)


@st.cache_data
def load_app_data():
    return load_social_music_data(DATA_DIR)


def established_users(users: Iterable[SocialUser]) -> List[SocialUser]:
    return [user for user in users if user.onboarding_status == "established"]


def new_users(users: Iterable[SocialUser]) -> List[SocialUser]:
    return [user for user in users if user.onboarding_status == "new"]


def render_profile_card(user: SocialUser, history_count: int) -> None:
    st.markdown(f"### {user.name}")
    st.write(f"User ID: `{user.user_id}`")
    st.write(f"Status: `{user.onboarding_status}`")
    if user.invited_by:
        st.write(f"Invited by: `{user.invited_by}`")
    st.write(f"Preferred genres: {', '.join(user.preferred_genres)}")
    st.write(f"Preferred moods: {', '.join(user.preferred_moods)}")
    st.write(
        "Target profile: "
        f"energy {user.energy_preference:.2f}, "
        f"tempo {user.tempo_preference:.0f}, "
        f"valence {user.valence_preference:.2f}"
    )
    st.write(f"Listening history events: `{history_count}`")


def render_recommendations(results) -> None:
    for index, result in enumerate(results, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {result.title}** by `{result.artist}`")
            metric_cols = st.columns(3)
            metric_cols[0].metric("Score", f"{result.score:.2f}")
            metric_cols[1].metric("Confidence", f"{result.confidence:.2f}")
            metric_cols[2].metric(
                "Weights",
                f"P {result.source_breakdown['personal_weight']:.2f} / S {result.source_breakdown['social_weight']:.2f}",
            )
            st.write("Why it appeared:")
            for reason in result.reasons[:5]:
                st.write(f"- {reason}")


def render_analytics(analytics: dict) -> None:
    cols = st.columns(4)
    cols[0].metric("Recommendations Sent", analytics["sent_count"])
    cols[1].metric("Successful Plays", analytics["successful_count"])
    cols[2].metric("Success Rate", f"{analytics['success_rate']:.2f}")
    cols[3].metric("Best Context", analytics["best_context"] or "N/A")


def render_existing_user_view(data, recommender: SocialRecommender, user_id: str) -> None:
    user = data.users[user_id]
    history = list(iter_user_history(data.listening_history, user_id))
    recommendations = recommender.recommend_for_user(user_id, k=5)
    analytics = summarize_user_analytics(data, user_id)

    left, right = st.columns([1, 2])
    with left:
        render_profile_card(user, len(history))
        st.markdown("### Existing User Context")
        st.write("This user already has listening history, so the system leans more heavily on personal taste signals.")
        st.write("Friends still matter, but they do not dominate the ranking.")
        render_analytics(analytics)

    with right:
        st.markdown("### Recommendations")
        render_recommendations(recommendations)


def render_new_user_view(data, recommender: SocialRecommender, user_id: str) -> None:
    user = data.users[user_id]
    history = list(iter_user_history(data.listening_history, user_id))
    inviter = data.users.get(user.invited_by) if user.invited_by else None
    friend_ids = sorted(data.friendships.get(user_id, set()))
    incoming_recs = [rec for rec in data.recommendations if rec.to_user_id == user_id]
    recommendations = recommender.recommend_for_user(user_id, k=5)

    st.markdown("### Onboarding Walkthrough")
    step_cols = st.columns(4)
    step_cols[0].info(f"1. Accept invite from `{user.invited_by}`")
    step_cols[1].info(f"2. Add {len(friend_ids)} friend(s)")
    step_cols[2].info("3. Enter starter taste preferences")
    step_cols[3].info("4. Generate cold-start recommendations")

    left, right = st.columns([1, 2])
    with left:
        render_profile_card(user, len(history))
        st.markdown("### Join Context")
        if inviter:
            st.write(f"Inviter: **{inviter.name}**")
        st.write("Connected friends:", ", ".join(friend_ids) if friend_ids else "No friends found")
        st.write(f"Incoming friend recommendations: `{len(incoming_recs)}`")
        st.write("Cold-start mode uses social signals more heavily because the user has limited history.")

    with right:
        st.markdown("### Recommendations After Joining")
        render_recommendations(recommendations)


def render_comparison_view(data, recommender: SocialRecommender, existing_user_id: str, new_user_id: str) -> None:
    existing_user = data.users[existing_user_id]
    new_user = data.users[new_user_id]
    existing_results = recommender.recommend_for_user(existing_user_id, k=3)
    new_results = recommender.recommend_for_user(new_user_id, k=3)

    left, right = st.columns(2)
    with left:
        st.markdown("### Existing User")
        render_profile_card(existing_user, len(list(iter_user_history(data.listening_history, existing_user_id))))
        st.write("Recommendation mode: established-user ranking")
        render_recommendations(existing_results)

    with right:
        st.markdown("### New Invited User")
        render_profile_card(new_user, len(list(iter_user_history(data.listening_history, new_user_id))))
        st.write("Recommendation mode: cold-start social ranking")
        render_recommendations(new_results)

    st.markdown("### What Changes Between Them")
    st.write("- Existing users rely more on their own history and taste profile.")
    st.write("- New users rely more on invite relationships, friend likes, and direct song recommendations.")
    st.write("- Confidence stays high in both cases, but the explanation reasons reveal which signals were actually used.")


def main() -> None:
    data = load_app_data()
    recommender = SocialRecommender(data)

    st.title("🎵 Social Music Recommender")
    st.write(
        "This demo shows how the same recommendation system behaves for an established user and a newly invited user."
    )

    established = established_users(data.users.values())
    onboarded = new_users(data.users.values())

    with st.sidebar:
        st.header("Demo Controls")
        view = st.radio(
            "Choose demo view",
            ["Existing user", "New user onboarding", "Compare both"],
        )
        selected_existing = st.selectbox(
            "Established user",
            options=established,
            index=0,
            format_func=lambda user: f"{user.name} ({user.user_id})",
        )
        selected_new = st.selectbox(
            "New user",
            options=onboarded,
            index=0,
            format_func=lambda user: f"{user.name} ({user.user_id})",
        )

    if view == "Existing user":
        render_existing_user_view(data, recommender, selected_existing.user_id)
    elif view == "New user onboarding":
        render_new_user_view(data, recommender, selected_new.user_id)
    else:
        render_comparison_view(
            data,
            recommender,
            selected_existing.user_id,
            selected_new.user_id,
        )

    st.markdown("---")
    st.markdown("### Reliability Summary")
    reliability = run_reliability_checks(data)
    rel_cols = st.columns(2)
    rel_cols[0].metric("Checks Passed", f"{reliability['passed']} / {reliability['total']}")
    with rel_cols[1]:
        for label, passed in reliability["checks"]:
            state = "PASS" if passed else "FAIL"
            st.write(f"- [{state}] {label}")


if __name__ == "__main__":
    main()
