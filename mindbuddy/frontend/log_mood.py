"""
MindBuddy Mood Logging Module
Handles mood entry logging functionality
"""

import streamlit as st
import time
from datetime import date, timedelta
from api_client import MindBuddyAPI, get_mood_emoji

def log_mood_interface(user_token):
    """Main mood logging interface"""
    st.markdown("### 📝 How are you feeling today?")
    
    # Check if already logged today
    if st.session_state.is_demo:
        has_logged = False  # Always allow logging in demo
    else:
        today_mood = MindBuddyAPI.get_today_mood(token=user_token)
        has_logged = today_mood.get('has_logged_today', False) if today_mood else False
    
    if has_logged:
        st.success("✅ You've already logged your mood today! You can update it below if needed.")
    
    # Enhanced mood logging form
    _display_mood_form(user_token)

def _display_mood_form(user_token):
    """Display the mood logging form"""
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    with st.form("mood_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mood_rating = _mood_rating_slider()
            energy_level = _energy_level_slider()
        
        with col2:
            anxiety_level = _anxiety_level_slider()
            log_date = _date_selector()
        
        notes = _notes_input()
        
        # Submit buttons
        submit_col1, submit_col2 = st.columns([3, 1])
        with submit_col1:
            submit_button = st.form_submit_button("💫 Log My Mood", use_container_width=True)
        with submit_col2:
            quick_log_button = st.form_submit_button("🎯 Quick Log", help="Log with current values", use_container_width=True)
        
        if submit_button or quick_log_button:
            _handle_mood_submission(mood_rating, energy_level, anxiety_level, log_date, notes, user_token)
    
    st.markdown('</div>', unsafe_allow_html=True)

def _mood_rating_slider():
    """Mood rating slider component"""
    st.markdown("#### 🌟 How's your mood?")
    return st.select_slider(
        "",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: f"{get_mood_emoji(x)} {x}/5",
        key="mood_slider",
        label_visibility="collapsed"
    )

def _energy_level_slider():
    """Energy level slider component"""
    st.markdown("#### ⚡ Energy level?")
    return st.select_slider(
        "",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: f"{'🔋' * x} {x}/5",
        key="energy_slider",
        label_visibility="collapsed"
    )

def _anxiety_level_slider():
    """Anxiety level slider component"""
    st.markdown("#### 🧘 Anxiety level?")
    return st.select_slider(
        "",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: f"{'😰' if x > 3 else '😌' if x < 3 else '😐'} {x}/5",
        key="anxiety_slider",
        label_visibility="collapsed"
    )

def _date_selector():
    """Date selector component"""
    st.markdown("#### 📅 Date")
    return st.date_input(
        "",
        value=date.today(),
        max_value=date.today(),
        min_value=date.today() - timedelta(days=7),
        key="mood_date",
        label_visibility="collapsed"
    )

def _notes_input():
    """Notes input component"""
    st.markdown("#### 📝 How was your day?")
    return st.text_area(
        "",
        placeholder="Share your thoughts, feelings, or anything notable about your day... ✨",
        height=120,
        max_chars=500,
        key="mood_notes",
        label_visibility="collapsed"
    )

def _handle_mood_submission(mood_rating, energy_level, anxiety_level, log_date, notes, user_token):
    """Handle mood form submission"""
    mood_data = {
        "date": log_date.isoformat(),
        "mood_rating": mood_rating,
        "energy_level": energy_level,
        "anxiety_level": anxiety_level,
        "notes": notes
    }
    
    with st.spinner("Saving your mood... ✨"):
        if st.session_state.is_demo:
            result = {"status": "success", "streak": {"current_streak": 6}}
            time.sleep(1)  # Simulate API call
        else:
            result = MindBuddyAPI.log_mood(mood_data, token=user_token)
    
    _handle_mood_result(result)

def _handle_mood_result(result):
    """Handle the result of mood logging"""
    if result and result.get('status') == 'success':
        st.success("🌟 Mood logged successfully!")
        streak_info = result.get('streak', {})
        
        # Show streak celebration
        current_streak = streak_info.get('current_streak', 0)
        if current_streak > 0:
            st.balloons()
            st.success(f"🔥 Amazing! You're on a {current_streak}-day streak!")
        
        # Auto-refresh
        time.sleep(2)
        st.rerun()
        
    elif result and 'error' in result:
        if 'already logged' in result['error']:
            st.warning("You've already logged your mood for this date. Thanks for staying consistent! 🌟")
        else:
            st.error(f"Error: {result['error']}")
    else:
        if not st.session_state.is_demo:
            st.error("Could not connect to MindBuddy. Please check if the server is running.")