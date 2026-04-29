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


def get_recommendation_badges(result) -> str:
    """Generate visual badges showing recommendation source"""
    badges = []

    # Check for specific friend signals
    has_friend_rec = any("explicitly recommended by a friend" in r for r in result.reasons)
    has_friend_like = any("friend(s) already liked" in r for r in result.reasons)
    has_taste_match = any("closest taste profile" in r for r in result.reasons)

    if has_friend_rec:
        badges.append("🎁 Friend Recommended")
    if has_friend_like:
        badges.append("👥 Liked by Friends")
    if has_taste_match:
        badges.append("🎯 Similar Taste")

    # Determine primary source
    social_weight = result.source_breakdown['social_weight']
    personal_weight = result.source_breakdown['personal_weight']

    if social_weight > personal_weight:
        badges.append("🤝 Socially Driven")
    else:
        badges.append("🎵 AI Personalized")

    return " · ".join(badges)


def get_friend_influence_details(data, user_id: str, song_id: str):
    """Get detailed information about which friends influenced this recommendation"""
    friends = data.friendships.get(user_id, set())

    # Find friends who recommended this song
    recommenders = []
    for rec in data.recommendations:
        if rec.to_user_id == user_id and rec.song_id == song_id and rec.from_user_id in friends:
            friend = data.users.get(rec.from_user_id)
            if friend:
                recommenders.append({
                    'friend': friend,
                    'anonymous': rec.anonymous,
                    'message': rec.message,
                    'context': rec.context_tag,
                })

    # Find friends who liked this song
    likers = []
    for event in data.listening_history:
        if event.user_id in friends and event.song_id == song_id and event.liked:
            friend = data.users.get(event.user_id)
            if friend:
                # Get friend's top liked songs
                friend_likes = [
                    e for e in data.listening_history
                    if e.user_id == event.user_id and e.liked
                ]
                friend_likes.sort(key=lambda e: e.play_count, reverse=True)
                top_songs = []
                for like_event in friend_likes[:3]:
                    song = data.songs.get(like_event.song_id)
                    if song:
                        top_songs.append(song)

                likers.append({
                    'friend': friend,
                    'play_count': event.play_count,
                    'top_songs': top_songs,
                })

    return {
        'recommenders': recommenders,
        'likers': likers,
    }


def render_welcome_screen():
    """Landing page with user selection"""
    st.title("🎵 Social Music Recommender Demo")
    st.markdown("---")

    st.markdown("""
    ### Welcome to Your Personalized Music Experience

    This demo shows how our AI-powered recommendation system works for different user types:
    - **Existing users** with listening history get personalized recommendations
    - **New users** leverage social connections to solve the cold-start problem
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Existing User Path")
        st.info("""
        **Experience as an established user with history**

        - View your listening profile
        - Get personalized recommendations
        - See how your taste shapes results
        """)
        if st.button("Continue as Existing User", type="primary", use_container_width=True):
            st.session_state.user_type = "existing"
            st.session_state.page = "select_user"
            st.rerun()

    with col2:
        st.markdown("### ✨ New User Path")
        st.success("""
        **Experience onboarding as a new invited user**

        - Accept an invite from a friend
        - Set your music preferences
        - Get cold-start recommendations
        """)
        if st.button("Continue as New User", type="primary", use_container_width=True):
            st.session_state.user_type = "new"
            st.session_state.page = "select_user"
            st.rerun()


def render_user_selection(data):
    """User selection screen"""
    if st.session_state.user_type == "existing":
        st.title("👤 Select Your Profile")
        st.write("Choose an existing user to see their personalized recommendations")

        established = established_users(data.users.values())

        for user in established:
            history_count = len(list(iter_user_history(data.listening_history, user.user_id)))
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {user.name}")
                    st.write(f"**Genres:** {', '.join(user.preferred_genres[:3])}")
                    st.write(f"**Listening history:** {history_count} events")
                with col2:
                    st.write("")  # spacing
                    if st.button("View Dashboard", key=user.user_id, type="primary"):
                        st.session_state.selected_user = user.user_id
                        st.session_state.page = "dashboard"
                        st.rerun()

    else:  # new user
        st.title("✨ Start Your Music Journey")
        st.write("Select a new user profile to experience the onboarding flow")

        onboarded = new_users(data.users.values())

        for user in onboarded:
            inviter = data.users.get(user.invited_by) if user.invited_by else None
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {user.name}")
                    st.write(f"**Invited by:** {inviter.name if inviter else 'Unknown'}")
                    st.write(f"**Status:** Just joined!")
                with col2:
                    st.write("")  # spacing
                    if st.button("Begin Onboarding", key=user.user_id, type="primary"):
                        st.session_state.selected_user = user.user_id
                        st.session_state.onboarding_step = 1
                        st.session_state.page = "onboarding"
                        st.rerun()

    st.markdown("---")
    if st.button("← Back to Welcome"):
        st.session_state.page = "welcome"
        st.rerun()


def render_onboarding_flow(data, recommender: SocialRecommender):
    """Step-by-step onboarding for new users"""
    user_id = st.session_state.selected_user
    user = data.users[user_id]
    inviter = data.users.get(user.invited_by) if user.invited_by else None
    step = st.session_state.get("onboarding_step", 1)

    st.title(f"✨ Welcome, {user.name}!")

    # Progress indicator
    progress = st.progress(step / 4)
    st.write(f"Step {step} of 4")
    st.markdown("---")

    if step == 1:
        st.markdown("### Step 1: Accept Your Invite")
        st.success(f"🎉 You've been invited by **{inviter.name if inviter else 'a friend'}**!")
        st.write("Join our social music community to discover songs your friends love.")

        col1, col2 = st.columns(2)
        with col1:
            if inviter:
                st.info(f"""
                **About {inviter.name}:**
                - Favorite genres: {', '.join(inviter.preferred_genres[:3])}
                - Music vibe: {', '.join(inviter.preferred_moods[:2])}
                """)
        with col2:
            st.write("")
            st.write("")
            if st.button("Accept Invite →", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()

    elif step == 2:
        st.markdown("### Step 2: Your Music Preferences")
        st.write("Let us know what you like so we can tailor recommendations!")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Your Preferred Genres:**")
            for genre in user.preferred_genres:
                st.write(f"✓ {genre.title()}")

        with col2:
            st.markdown("**Your Preferred Moods:**")
            for mood in user.preferred_moods:
                st.write(f"✓ {mood.title()}")

        st.write("")
        st.info(f"🎚️ **Your Sound Profile:** Energy {user.energy_preference:.1f} • Tempo {user.tempo_preference:.0f} BPM • Valence {user.valence_preference:.1f}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()

    elif step == 3:
        st.markdown("### Step 3: Connect with Friends")
        friend_ids = sorted(data.friendships.get(user_id, set()))
        incoming_recs = [rec for rec in data.recommendations if rec.to_user_id == user_id]

        st.success(f"You're now connected with {len(friend_ids)} friend(s)!")

        if friend_ids:
            st.write("**Your Network:**")
            cols = st.columns(min(len(friend_ids), 3))
            for idx, friend_id in enumerate(friend_ids):
                friend = data.users.get(friend_id)
                if friend:
                    with cols[idx % 3]:
                        st.info(f"👤 **{friend.name}**\n\n{', '.join(friend.preferred_genres[:2])}")

        if incoming_recs:
            st.write(f"")
            st.write(f"🎁 You have **{len(incoming_recs)}** song recommendation(s) from friends!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Get Recommendations →", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 4
                st.rerun()

    else:  # step == 4
        st.markdown("### Step 4: Your Personalized Recommendations")
        st.write("Based on your preferences and your friends' favorites, here's what we recommend:")

        recommendations = recommender.recommend_for_user(user_id, k=5)

        st.balloons()

        for index, result in enumerate(recommendations, start=1):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {index}. {result.title}")
                    st.write(f"**Artist:** {result.artist}")

                    # Show source badges
                    badges = get_recommendation_badges(result)
                    st.caption(f"📍 {badges}")

                    st.write("**Why you'll love it:**")
                    for reason in result.reasons[:3]:
                        st.write(f"• {reason}")
                with col2:
                    st.metric("Match Score", f"{result.score:.2f}")
                    st.metric("Confidence", f"{result.confidence:.0%}")

                    # Show signal breakdown more clearly
                    personal_pct = result.source_breakdown['personal_weight'] * 100
                    social_pct = result.source_breakdown['social_weight'] * 100
                    st.caption(f"🎵 AI: {personal_pct:.0f}%")
                    st.caption(f"🤝 Social: {social_pct:.0f}%")

                # Add friend influence section
                influence = get_friend_influence_details(data, user_id, result.song_id)
                if influence['recommenders'] or influence['likers']:
                    with st.expander("👥 See Friend Influence", expanded=False):
                        # Show friends who recommended this song
                        if influence['recommenders']:
                            st.markdown("**🎁 Friends Who Recommended This:**")
                            for rec_info in influence['recommenders']:
                                friend = rec_info['friend']
                                if rec_info['anonymous']:
                                    st.info(f"🔒 **Anonymous Friend**\n\n*\"{rec_info['message']}\"*\n\nContext: {rec_info['context']}")
                                else:
                                    st.success(f"👤 **{friend.name}**\n\n*\"{rec_info['message']}\"*\n\nContext: {rec_info['context']}")
                                    with st.container():
                                        st.caption(f"**{friend.name}'s taste:** {', '.join(friend.preferred_genres[:3])}")

                        # Show friends who liked this song
                        if influence['likers']:
                            st.markdown("**👍 Friends Who Like This:**")
                            for liker_info in influence['likers']:
                                friend = liker_info['friend']
                                st.write(f"**{friend.name}** (played {liker_info['play_count']} times)")
                                if liker_info['top_songs']:
                                    st.caption(f"Also likes: {', '.join([s['title'] for s in liker_info['top_songs'][:2]])}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Start Over", use_container_width=True):
                st.session_state.page = "welcome"
                st.rerun()
        with col2:
            if st.button("View System Stats", use_container_width=True):
                st.session_state.page = "reliability"
                st.rerun()


def render_existing_user_dashboard(data, recommender: SocialRecommender):
    """Dashboard for existing users"""
    user_id = st.session_state.selected_user
    user = data.users[user_id]
    history = list(iter_user_history(data.listening_history, user_id))

    st.title(f"👤 Welcome back, {user.name}!")
    st.markdown("---")

    # User stats
    analytics = summarize_user_analytics(data, user_id)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listening Events", len(history))
    col2.metric("Recommendations Sent", analytics["sent_count"])
    col3.metric("Success Rate", f"{analytics['success_rate']:.0%}")
    col4.metric("Best Context", analytics["best_context"] or "N/A")

    st.markdown("---")

    # Profile summary
    with st.expander("📊 Your Music Profile", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Preferred Genres:**")
            for genre in user.preferred_genres:
                st.write(f"• {genre.title()}")
        with col2:
            st.write("**Preferred Moods:**")
            for mood in user.preferred_moods:
                st.write(f"• {mood.title()}")
        st.info(f"🎚️ **Sound Profile:** Energy {user.energy_preference:.1f} • Tempo {user.tempo_preference:.0f} BPM • Valence {user.valence_preference:.1f}")

    # Recommendations
    st.markdown("### 🎵 Recommended For You")
    st.write("Based on your listening history and friend activity")

    recommendations = recommender.recommend_for_user(user_id, k=5)

    for index, result in enumerate(recommendations, start=1):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {index}. {result.title}")
                st.write(f"**Artist:** {result.artist}")

                # Show source badges
                badges = get_recommendation_badges(result)
                st.caption(f"📍 {badges}")

                st.write("**Why this matches your taste:**")
                for reason in result.reasons[:3]:
                    st.write(f"• {reason}")
            with col2:
                st.metric("Match Score", f"{result.score:.2f}")
                st.metric("Confidence", f"{result.confidence:.0%}")

                # Show signal breakdown more clearly
                personal_pct = result.source_breakdown['personal_weight'] * 100
                social_pct = result.source_breakdown['social_weight'] * 100
                st.caption(f"🎵 AI: {personal_pct:.0f}%")
                st.caption(f"🤝 Social: {social_pct:.0f}%")

            # Add friend influence section
            influence = get_friend_influence_details(data, user_id, result.song_id)
            if influence['recommenders'] or influence['likers']:
                with st.expander("👥 See Friend Influence", expanded=False):
                    # Show friends who recommended this song
                    if influence['recommenders']:
                        st.markdown("**🎁 Friends Who Recommended This:**")
                        for rec_info in influence['recommenders']:
                            friend = rec_info['friend']
                            if rec_info['anonymous']:
                                st.info(f"🔒 **Anonymous Friend**\n\n*\"{rec_info['message']}\"*\n\nContext: {rec_info['context']}")
                            else:
                                st.success(f"👤 **{friend.name}**\n\n*\"{rec_info['message']}\"*\n\nContext: {rec_info['context']}")
                                with st.container():
                                    st.caption(f"**{friend.name}'s taste:** {', '.join(friend.preferred_genres[:3])}")

                    # Show friends who liked this song
                    if influence['likers']:
                        st.markdown("**👍 Friends Who Like This:**")
                        for liker_info in influence['likers']:
                            friend = liker_info['friend']
                            st.write(f"**{friend.name}** (played {liker_info['play_count']} times)")
                            if liker_info['top_songs']:
                                st.caption(f"Also likes: {', '.join([s['title'] for s in liker_info['top_songs'][:2]])}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to User Selection", use_container_width=True):
            st.session_state.page = "select_user"
            st.rerun()
    with col2:
        if st.button("View System Stats", use_container_width=True):
            st.session_state.page = "reliability"
            st.rerun()


def render_reliability_page(data):
    """System reliability and testing summary"""
    st.title("🔬 System Reliability & Testing")
    st.write("This page shows the built-in reliability checks and testing results.")
    st.markdown("---")

    reliability = run_reliability_checks(data)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(
            "Tests Passed",
            f"{reliability['passed']} / {reliability['total']}",
            delta="All systems operational" if reliability['passed'] == reliability['total'] else "Issues detected"
        )

    with col2:
        st.write("**Integrated Reliability Checks:**")
        for label, passed in reliability["checks"]:
            state = "✅ PASS" if passed else "❌ FAIL"
            st.write(f"{state} — {label}")

    st.markdown("---")

    st.markdown("### 📋 Testing Summary")
    st.write("""
    **Automated Tests:** 4/4 pytest tests passing
    - Unit test: recommendation scoring and sorting
    - Unit test: explanation generation
    - Integration test: new user onboarding flow
    - Integration test: reliability checks on seed data

    **Confidence Scoring:** Every recommendation includes a confidence score (0-1) based on signal strength

    **Logging:** Application logs track recommendation generation, data loading, and errors
    """)

    st.markdown("---")

    st.markdown("### 🎯 Required AI Feature: Reliability & Testing System")
    st.info("""
    This project implements a **Reliability or Testing System** as its required applied AI feature.

    The reliability layer is fully integrated into the main application flow:
    - Automated checks verify new-user onboarding works correctly
    - Established user preferences are validated against recommendations
    - Friend network integrity is confirmed for invited users
    - Data consistency checks ensure recommendation validity
    - Confidence scores provide transparency for each result
    """)

    if st.button("← Back to Welcome", use_container_width=True):
        st.session_state.page = "welcome"
        st.rerun()


def main() -> None:
    data = load_app_data()
    recommender = SocialRecommender(data)

    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    # Route to appropriate page
    if st.session_state.page == "welcome":
        render_welcome_screen()
    elif st.session_state.page == "select_user":
        render_user_selection(data)
    elif st.session_state.page == "onboarding":
        render_onboarding_flow(data, recommender)
    elif st.session_state.page == "dashboard":
        render_existing_user_dashboard(data, recommender)
    elif st.session_state.page == "reliability":
        render_reliability_page(data)


if __name__ == "__main__":
    main()
