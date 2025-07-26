# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import json
import time

# Page configuration with healing theme
st.set_page_config(
    page_title="🌸 MindBuddy - Your Mental Wellness Companion",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for healing aesthetics
st.markdown("""
<style>
    /* Import beautiful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Custom card styling */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Healing color palette */
    :root {
        --healing-pink: #FFB6C1;
        --healing-lavender: #E6E6FA;
        --healing-mint: #98FB98;
        --healing-peach: #FFEAA7;
        --healing-blue: #74B9FF;
    }
    
    /* Typography */
    .big-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FFB6C1, #FFF0F5);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .mood-emoji {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FFB6C1, #FF69B4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FFB6C1, #FF69B4);
    }
    
    /* Chart styling */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000/api"

class MindBuddyAPI:
    """API client for MindBuddy backend"""
    
    @staticmethod
    def log_mood(mood_data):
        """Log mood entry"""
        try:
            response = requests.post(f"{API_BASE_URL}/mood/", json=mood_data)
            return response.json() if response.status_code in [200, 201] else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_mood_history(days=30):
        """Get mood history"""
        try:
            response = requests.get(f"{API_BASE_URL}/mood/history/?days={days}")
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_streak_info():
        """Get streak information"""
        try:
            response = requests.get(f"{API_BASE_URL}/mood/streak/")
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_today_mood():
        """Get today's mood"""
        try:
            response = requests.get(f"{API_BASE_URL}/mood/today/")
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def chat_with_buddy(message):
        """Chat with MindBuddy"""
        try:
            response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None

def get_mood_emoji(rating):
    """Get emoji for mood rating"""
    mood_emojis = {
        1: "😢", 2: "😔", 3: "😐", 4: "😊", 5: "😄"
    }
    return mood_emojis.get(rating, "😐")

def get_mood_color(rating):
    """Get color for mood rating"""
    mood_colors = {
        1: "#FF6B6B", 2: "#FFA726", 3: "#FFD54F", 4: "#66BB6A", 5: "#42A5F5"
    }
    return mood_colors.get(rating, "#FFD54F")

def create_mood_chart(data):
    """Create beautiful mood trend chart"""
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
    
    # Add mood line
    fig.add_trace(go.Scatter(
        x=df_with_data['date'],
        y=df_with_data['mood_rating'],
        mode='lines+markers',
        name='Mood Rating',
        line=dict(color='#FF69B4', width=3, shape='spline'),
        marker=dict(size=8, color='#FF1493'),
        hovertemplate='<b>%{x}</b><br>Mood: %{y}/5<extra></extra>'
    ))
    
    # Customize layout
    fig.update_layout(
        title={
            'text': '🌈 Your Mood Journey',
            'x': 0.5,
            'font': {'size': 24, 'family': 'Poppins'}
        },
        xaxis_title="Date",
        yaxis_title="Mood Rating",
        yaxis=dict(range=[0.5, 5.5], tickmode='linear', dtick=1),
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter"),
        hovermode='x unified'
    )
    
    # Add subtle grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

def create_multi_metric_chart(data):
    """Create multi-metric comparison chart"""
    if not data or not data.get('chart_data'):
        return None
    
    df = pd.DataFrame(data['chart_data'])
    df['date'] = pd.to_datetime(df['date'])
    df_with_data = df[df['has_entry'] == True].copy()
    
    if df_with_data.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('🌟 Mood Rating', '⚡ Energy Level', '😰 Anxiety Level'),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # Add mood trace
    fig.add_trace(
        go.Scatter(
            x=df_with_data['date'], y=df_with_data['mood_rating'],
            mode='lines+markers', name='Mood', line=dict(color='#FF69B4', width=2),
            marker=dict(size=6)
        ), row=1, col=1
    )
    
    # Add energy trace
    fig.add_trace(
        go.Scatter(
            x=df_with_data['date'], y=df_with_data['energy_level'],
            mode='lines+markers', name='Energy', line=dict(color='#42A5F5', width=2),
            marker=dict(size=6)
        ), row=2, col=1
    )
    
    # Add anxiety trace (inverted scale for better UX)
    fig.add_trace(
        go.Scatter(
            x=df_with_data['date'], y=df_with_data['anxiety_level'],
            mode='lines+markers', name='Anxiety', line=dict(color='#FFA726', width=2),
            marker=dict(size=6)
        ), row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '📊 Comprehensive Wellness Tracking',
            'x': 0.5,
            'font': {'size': 20, 'family': 'Poppins'}
        },
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter")
    )
    
    # Update y-axes ranges
    fig.update_yaxes(range=[0.5, 5.5], row=1, col=1)
    fig.update_yaxes(range=[0.5, 5.5], row=2, col=1)
    fig.update_yaxes(range=[0.5, 5.5], row=3, col=1)
    
    return fig

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="big-title">🌸 MindBuddy</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Personal Mental Wellness Companion</p>', unsafe_allow_html=True)
    
    # Navigation
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "📝 Log Mood", "📊 Analytics", "💬 Chat with Buddy"])
    
    with tab1:
        st.markdown("### 🌟 Welcome to Your Wellness Dashboard")
        
        # Get data
        streak_data = MindBuddyAPI.get_streak_info()
        today_mood = MindBuddyAPI.get_today_mood()
        mood_history = MindBuddyAPI.get_mood_history(7)  # Last 7 days
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_streak = streak_data.get('current_streak', 0) if streak_data else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="mood-emoji">🔥</div>
                <h3>{current_streak}</h3>
                <p>Current Streak</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            longest_streak = streak_data.get('longest_streak', 0) if streak_data else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="mood-emoji">🏆</div>
                <h3>{longest_streak}</h3>
                <p>Best Streak</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_entries = streak_data.get('total_entries', 0) if streak_data else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="mood-emoji">📈</div>
                <h3>{total_entries}</h3>
                <p>Total Entries</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            has_logged_today = today_mood.get('has_logged_today', False) if today_mood else False
            today_emoji = "✅" if has_logged_today else "⏰"
            today_text = "Logged!" if has_logged_today else "Pending"
            st.markdown(f"""
            <div class="metric-card">
                <div class="mood-emoji">{today_emoji}</div>
                <h3>{today_text}</h3>
                <p>Today's Mood</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Today's mood display
        if has_logged_today and today_mood.get('today_mood'):
            mood_data = today_mood['today_mood']
            st.markdown("### 🌅 Today's Wellness Check")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                mood_rating = mood_data.get('mood_rating', 3)
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 4rem;">{get_mood_emoji(mood_rating)}</div>
                    <h4>Mood: {mood_rating}/5</h4>
                    <p>{mood_data.get('mood_display', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                energy_level = mood_data.get('energy_level', 3)
                if energy_level:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 4rem;">⚡</div>
                        <h4>Energy: {energy_level}/5</h4>
                        <p>{mood_data.get('energy_display', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                anxiety_level = mood_data.get('anxiety_level', 3)
                if anxiety_level:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 4rem;">🧘</div>
                        <h4>Anxiety: {anxiety_level}/5</h4>
                        <p>{mood_data.get('anxiety_display', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if mood_data.get('notes'):
                st.markdown("#### 📝 Today's Notes")
                st.info(mood_data['notes'])
        
        # Weekly mood chart
        if mood_history and mood_history.get('chart_data'):
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
                    st.metric("Average Mood", f"{avg_mood:.1f}/5")
                with col2:
                    tracking_pct = stats.get('tracking_percentage', 0)
                    st.metric("Tracking Progress", f"{tracking_pct:.0f}%")
                with col3:
                    total_entries = stats.get('total_entries', 0)
                    st.metric("Entries This Week", total_entries)
    
    with tab2:
        st.markdown("### 📝 How are you feeling today?")
        
        # Check if already logged today
        today_mood = MindBuddyAPI.get_today_mood()
        has_logged = today_mood.get('has_logged_today', False) if today_mood else False
        
        if has_logged:
            st.success("✅ You've already logged your mood today! You can update it below if needed.")
        
        # Mood logging form
        with st.form("mood_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mood_rating = st.select_slider(
                    "🌟 Overall Mood",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{get_mood_emoji(x)} {x}/5"
                )
                
                energy_level = st.select_slider(
                    "⚡ Energy Level",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{x}/5"
                )
            
            with col2:
                anxiety_level = st.select_slider(
                    "🧘 Anxiety Level",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{x}/5"
                )
                
                log_date = st.date_input(
                    "📅 Date",
                    value=date.today(),
                    max_value=date.today(),
                    min_value=date.today() - timedelta(days=7)
                )
            
            notes = st.text_area(
                "📝 Notes (Optional)",
                placeholder="How was your day? Any thoughts or feelings you'd like to record?",
                max_chars=500
            )
            
            submit_button = st.form_submit_button("💫 Log My Mood", use_container_width=True)
            
            if submit_button:
                mood_data = {
                    "date": log_date.isoformat(),
                    "mood_rating": mood_rating,
                    "energy_level": energy_level,
                    "anxiety_level": anxiety_level,
                    "notes": notes
                }
                
                with st.spinner("Saving your mood..."):
                    result = MindBuddyAPI.log_mood(mood_data)
                
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
                        st.warning("You've already logged your mood for this date. Use the update feature instead!")
                    else:
                        st.error(f"Error: {result['error']}")
                else:
                    st.error("Could not connect to MindBuddy. Please check if the server is running.")
    
    with tab3:
        st.markdown("### 📊 Your Wellness Analytics")
        
        # Time period selector
        period = st.selectbox(
            "📅 Select Time Period",
            options=[7, 14, 30, 60, 90],
            format_func=lambda x: f"Last {x} days",
            index=2  # Default to 30 days
        )
        
        # Get mood history
        with st.spinner("Loading your wellness data..."):
            mood_history = MindBuddyAPI.get_mood_history(period)
        
        if mood_history and mood_history.get('chart_data'):
            # Statistics overview
            stats = mood_history.get('statistics', {})
            if stats:
                st.markdown("#### 📈 Period Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_mood = stats.get('average_mood', 0)
                    st.metric(
                        "Average Mood", 
                        f"{avg_mood:.1f}/5",
                        delta=f"{get_mood_emoji(round(avg_mood))}"
                    )
                
                with col2:
                    tracking_pct = stats.get('tracking_percentage', 0)
                    st.metric("Tracking Consistency", f"{tracking_pct:.0f}%")
                
                with col3:
                    best_mood = stats.get('best_mood', 0)
                    st.metric("Best Mood", f"{best_mood}/5")
                
                with col4:
                    total_entries = stats.get('total_entries', 0)
                    st.metric("Total Entries", total_entries)
            
            # Main mood chart
            st.markdown("#### 🌈 Mood Trend Analysis")
            fig = create_mood_chart(mood_history)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="mood_trend_chart")
            
            # Multi-metric chart
            st.markdown("#### 📊 Comprehensive Wellness Tracking")
            multi_fig = create_multi_metric_chart(mood_history)
            if multi_fig:
                st.plotly_chart(multi_fig, use_container_width=True, key="multi_metric_chart")
            
            # Insights section
            st.markdown("#### 💡 Wellness Insights")
            
            chart_data = mood_history['chart_data']
            entries_with_data = [entry for entry in chart_data if entry['has_entry']]
            
            if entries_with_data:
                # Recent trend analysis
                recent_moods = [entry['mood_rating'] for entry in entries_with_data[-7:]]
                if len(recent_moods) >= 3:
                    trend = "improving" if recent_moods[-1] > recent_moods[0] else "declining" if recent_moods[-1] < recent_moods[0] else "stable"
                    trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
                    
                    st.info(f"{trend_emoji} Your mood trend over the last week appears to be **{trend}**.")
                
                # Consistency insight
                consistency = stats.get('tracking_percentage', 0)
                if consistency >= 80:
                    st.success("🌟 Excellent tracking consistency! You're building a great habit.")
                elif consistency >= 60:
                    st.info("👍 Good tracking consistency! Keep up the momentum.")
                else:
                    st.warning("💪 Try to log your mood more regularly for better insights.")
                
                # Mood distribution
                mood_counts = {}
                for entry in entries_with_data:
                    mood = entry['mood_rating']
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
                
                most_common_mood = max(mood_counts, key=mood_counts.get)
                st.info(f"{get_mood_emoji(most_common_mood)} Your most common mood rating is **{most_common_mood}/5**.")
        
        else:
            st.info("📊 Start logging your mood to see beautiful analytics here!")
            st.markdown("Use the **Log Mood** tab to get started on your wellness journey.")
    
    with tab4:
        st.markdown("### 💬 Chat with MindBuddy")
        st.markdown("*Your compassionate AI companion is here to listen and support you.*")
        
        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Hello! I'm MindBuddy 🌸 I'm here to listen and support you on your wellness journey. How are you feeling today?"}
            ]
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Share what's on your mind..."):
            # Add user message to chat history
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("MindBuddy is thinking..."):
                    response = MindBuddyAPI.chat_with_buddy(prompt)
                
                if response and response.get('assistant_response'):
                    assistant_message = response['assistant_response']['content']
                    st.markdown(assistant_message)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_message})
                else:
                    error_message = "I'm sorry, I'm having trouble connecting right now. Please make sure the MindBuddy server is running."
                    st.error(error_message)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_message})
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Hello! I'm MindBuddy 🌸 I'm here to listen and support you. How are you feeling today?"}
            ]
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Made with 💖 for your mental wellness journey | MindBuddy v1.0"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()