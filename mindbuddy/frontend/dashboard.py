"""
MindBuddy Dashboard Module
Displays the main dashboard with wellness metrics and overview
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from api_client import MindBuddyAPI, get_mood_emoji

def dashboard_interface(user_token):
    """Main dashboard interface"""
    st.markdown("### 🏠 Welcome to Your Wellness Dashboard")
    
    # Get data
    if st.session_state.is_demo:
        streak_data, today_mood, mood_history = _get_demo_data()
    else:
        streak_data = MindBuddyAPI.get_streak_info(token=user_token)
        today_mood = MindBuddyAPI.get_today_mood(token=user_token)
        mood_history = MindBuddyAPI.get_mood_history(7, token=user_token)
    
    # Enhanced metrics row
    _display_metrics_row(streak_data, today_mood)
    
    # Today's mood display
    if today_mood and today_mood.get('has_logged_today') and today_mood.get('today_mood'):
        _display_todays_mood(today_mood['today_mood'])
    
    # Weekly mood chart
    if mood_history and mood_history.get('chart_data'):
        _display_weekly_chart(mood_history)

def _get_demo_data():
    """Generate demo data for dashboard"""
    streak_data = {"current_streak": 5, "longest_streak": 12, "total_entries": 28}
    today_mood = {"has_logged_today": True, "today_mood": {
        "mood_rating": 4, "energy_level": 3, "anxiety_level": 2,
        "mood_display": "Good", "energy_display": "Moderate", "anxiety_display": "Low",
        "notes": "Had a productive day at work and went for a nice walk in the evening."
    }}
    mood_history = {
        "chart_data": [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
             "mood_rating": 3+i%3, "energy_level": 2+i%4, "anxiety_level": 4-i%3, "has_entry": True}
            for i in range(7, 0, -1)
        ],
        "statistics": {"average_mood": 3.8, "tracking_percentage": 85, "total_entries": 7}
    }
    return streak_data, today_mood, mood_history

def _display_metrics_row(streak_data, today_mood):
    """Display the main metrics row"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_streak = streak_data.get('current_streak', 0) if streak_data else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="mood-emoji">🔥</div>
            <h2 style="margin-bottom: 0.5rem; color: #ffffff;">{current_streak}</h2>
            <p style="color: #b8b8b8; margin: 0;">Current Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        longest_streak = streak_data.get('longest_streak', 0) if streak_data else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="mood-emoji">🏆</div>
            <h2 style="margin-bottom: 0.5rem; color: #ffffff;">{longest_streak}</h2>
            <p style="color: #b8b8b8; margin: 0;">Best Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_entries = streak_data.get('total_entries', 0) if streak_data else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="mood-emoji">📈</div>
            <h2 style="margin-bottom: 0.5rem; color: #ffffff;">{total_entries}</h2>
            <p style="color: #b8b8b8; margin: 0;">Total Entries</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        has_logged_today = today_mood.get('has_logged_today', False) if today_mood else False
        today_emoji = "✅" if has_logged_today else "⏰"
        today_text = "Logged!" if has_logged_today else "Pending"
        st.markdown(f"""
        <div class="metric-card">
            <div class="mood-emoji">{today_emoji}</div>
            <h2 style="margin-bottom: 0.5rem; color: #ffffff;">{today_text}</h2>
            <p style="color: #b8b8b8; margin: 0;">Today's Mood</p>
        </div>
        """, unsafe_allow_html=True)

def _display_todays_mood(mood_data):
    """Display today's mood information"""
    st.markdown("### 🌅 Today's Wellness Check")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mood_rating = mood_data.get('mood_rating', 3)
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{get_mood_emoji(mood_rating)}</div>
            <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Mood: {mood_rating}/5</h3>
            <p style="color: #b8b8b8;">{mood_data.get('mood_display', '')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        energy_level = mood_data.get('energy_level', 3)
        if energy_level:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">⚡</div>
                <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Energy: {energy_level}/5</h3>
                <p style="color: #b8b8b8;">{mood_data.get('energy_display', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        anxiety_level = mood_data.get('anxiety_level', 3)
        if anxiety_level:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🧘</div>
                <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Anxiety: {anxiety_level}/5</h3>
                <p style="color: #b8b8b8;">{mood_data.get('anxiety_display', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if mood_data.get('notes'):
        st.markdown("#### 📝 Today's Notes")
        st.markdown(f"""
        <div class="custom-card">
            <p style="color: #ffffff; font-style: italic; font-size: 1.1rem;">"{mood_data['notes']}"</p>
        </div>
        """, unsafe_allow_html=True)

def _display_weekly_chart(mood_history):
    """Display the weekly mood chart"""
    st.markdown("### 📊 Your Week at a Glance")
    fig = create_mood_chart(mood_history)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="weekly_mood_chart")
    
    # Weekly stats
    stats = mood_history.get('statistics', {})
    if stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_mood = stats.get('average_mood', 0)
            st.metric("Average Mood", f"{avg_mood:.1f}/5", delta="This week")
        with col2:
            tracking_pct = stats.get('tracking_percentage', 0)
            st.metric("Tracking Progress", f"{tracking_pct:.0f}%", delta="Consistency")
        with col3:
            total_entries = stats.get('total_entries', 0)
            st.metric("Entries This Week", total_entries, delta="Logged days")

def create_mood_chart(data):
    """Create beautiful mood trend chart with dark theme"""
    if not data or not data.get('chart_data'):
        return None
    
    df = pd.DataFrame(data['chart_data'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter entries with data
    df_with_data = df[df['has_entry'] == True].copy()
    
    if df_with_data.empty:
        return None
    
    # Create the mood trend chart
    fig = go.Figure()
    
    # Add mood line with gradient
    fig.add_trace(go.Scatter(
        x=df_with_data['date'],
        y=df_with_data['mood_rating'],
        mode='lines+markers',
        name='Mood Rating',
        line=dict(color='#667eea', width=4, shape='spline'),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Mood: %{y}/5<extra></extra>',
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # Customize layout for dark theme
    fig.update_layout(
        title={
            'text': '🌈 Your Mood Journey',
            'x': 0.5,
            'font': {'size': 28, 'family': 'Poppins', 'color': 'white'}
        },
        xaxis_title="Date",
        yaxis_title="Mood Rating",
        yaxis=dict(range=[0.5, 5.5], tickmode='linear', dtick=1),
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color='white'),
        hovermode='x unified'
    )
    
    # Dark theme grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    return fig