"""
MindBuddy - Main Execution File
This is the entry point of the application that handles routing and session management.
"""

import streamlit as st
from datetime import datetime
import time

# Import custom modules
from auth import auth_interface
from chat import chat_interface
from dashboard import dashboard_interface
from log_mood import log_mood_interface
from analytics import analytics_interface
from api_client import MindBuddyAPI

# Page configuration with healing theme
st.set_page_config(
    page_title="🌸 MindBuddy - Your Mental Wellness Companion",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with dark healing theme
st.markdown("""
<style>
    /* Import beautiful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&family=Nunito:wght@300;400;500;600;700&display=swap');
    
    /* Dark healing theme */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Custom card styling */
    .custom-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    
    /* Clean chat interface */
    .chat-interface {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .chat-messages {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .message-bubble {
        margin: 1rem 0;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        font-family: 'Inter', sans-serif;
        line-height: 1.5;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .assistant-bubble {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        margin-right: 20%;
        border-bottom-left-radius: 5px;
    }
    
    .chat-input-container {
        display: flex;
        gap: 0.5rem;
        align-items: flex-end;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .logout-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 107, 107, 0.9);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .logout-btn:hover {
        background: rgba(255, 107, 107, 1);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    /* Healing color palette */
    :root {
        --healing-pink: #FFB6C1;
        --healing-lavender: #E6E6FA;
        --healing-mint: #98FB98;
        --healing-peach: #FFEAA7;
        --healing-blue: #74B9FF;
        --dark-primary: #1a1a2e;
        --dark-secondary: #16213e;
        --dark-accent: #0f3460;
    }
    
    /* Typography */
    .big-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2, #38ef7d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        color: #b8b8b8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #ffffff;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
    }
    
    .mood-emoji {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        font-family: 'Nunito', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        min-height: 60px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(45deg, #5a6fd8, #6b42a0);
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 8px;
        border-radius: 4px;
    }
    
    .stSlider > div > div > div > div > div {
        background: white;
        border: 3px solid #667eea;
        width: 25px;
        height: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #11998e, #38ef7d);
    }
    
    /* Enhanced Auth form styling */
    .auth-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
        backdrop-filter: blur(25px);
        border-radius: 30px;
        padding: 4rem 3rem;
        margin: 3rem auto;
        max-width: 450px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .auth-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2, #38ef7d);
        opacity: 0.8;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .auth-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.2rem;
        font-weight: 600;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        font-family: 'Inter', sans-serif;
        color: #b8b8b8;
        font-size: 1rem;
        font-weight: 300;
    }
    
    .auth-form-field {
        margin-bottom: 1.5rem;
    }
    
    .auth-form-field label {
        color: #ffffff;
        font-family: 'Nunito', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        color: white;
        font-family: 'Inter', sans-serif;
        padding: 0.8rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Tab styling */
    .stTabs > div > div > div > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 0.5rem;
        color: #ffffff;
        font-family: 'Nunito', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #5a6fd8, #6b42a0);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'user_token' not in st.session_state:
        st.session_state.user_token = None
    if 'is_demo' not in st.session_state:
        st.session_state.is_demo = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

def handle_logout():
    """Handle user logout"""
    # Create a hidden button to handle logout via JavaScript
    st.markdown(f'''
    <button class="logout-btn" onclick="window.location.reload()">🚪 Logout</button>
    ''', unsafe_allow_html=True)
    
    # Check for logout action
    if st.button("", key="hidden_logout", help="Hidden logout button"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Authentication check
    if not st.session_state.is_authenticated:
        # Header for auth page
        st.markdown('<h1 class="big-title">🌸 MindBuddy</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Your Personal Mental Wellness Companion</p>', unsafe_allow_html=True)
        
        auth_interface()
        return
    
    # Main app for authenticated users
    handle_logout()
    
    # Header
    st.markdown('<h1 class="big-title">🌸 MindBuddy</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Welcome back, {st.session_state.username}! ✨</p>', unsafe_allow_html=True)
    
    # Navigation - Chat moved to first position
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat with Buddy", "🏠 Dashboard", "📝 Log Mood", "📊 Analytics"])
    
    # Get user token for API calls
    user_token = st.session_state.user_token if not st.session_state.is_demo else None
    
    with tab1:
        chat_interface(user_token)
    
    with tab2:
        dashboard_interface(user_token)
    
    with tab3:
        log_mood_interface(user_token)
    
    with tab4:
        analytics_interface(user_token)

    # Enhanced footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #b8b8b8; font-size: 0.9rem; font-family: Inter;'>
            <p>Made with 💖 for your mental wellness journey</p>
            <p>🌸 MindBuddy v2.0 - Enhanced Edition ✨</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()