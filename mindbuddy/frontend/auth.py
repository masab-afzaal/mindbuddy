"""
MindBuddy Authentication Module
Handles user login, registration, and authentication UI with backend integration
"""

import streamlit as st
import time
import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000/api"  # Adjust to your Django server

class MindBuddyAPI:
    """API client for MindBuddy backend"""
    
    @staticmethod
    def login(username, password):
        """Login user and return access token"""
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login/", {
                'name': username,
                'password': password
            })
            
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    @staticmethod
    def register(username, password):
        """Register new user and return access token"""
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register/", {
                'name': username,
                'password': password,
                'password_confirm': password  # Assuming same password for confirmation
            })
            
            if response.status_code == 201:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    @staticmethod
    def logout():
        """Logout user"""
        try:
            if 'user_token' in st.session_state:
                requests.post(f"{API_BASE_URL}/auth/logout/", 
                            headers={'Authorization': f'Token {st.session_state.user_token}'})
        except requests.exceptions.RequestException:
            pass  # Silent fail for logout
        finally:
            # Clear session regardless of API call success
            _clear_session()

def auth_interface():
    """Enhanced authentication interface"""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="auth-header">
        <h1 class="auth-title">🌸 Welcome to MindBuddy</h1>
        <p class="auth-subtitle">Your journey to better mental wellness starts here</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with auth_tab1:
        _login_form()
    
    with auth_tab2:
        _register_form()
    
    st.markdown('</div>', unsafe_allow_html=True)

def _login_form():
    """Login form component"""
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            login_btn = st.form_submit_button("🚀 Sign In", use_container_width=True)
        with col2:
            demo_btn = st.form_submit_button("🎯 Try Demo", use_container_width=True)
        
        if login_btn:
            _handle_login(username, password)
        
        if demo_btn:
            _handle_demo_login()

def _register_form():
    """Registration form component"""
    with st.form("register_form", clear_on_submit=False):
        new_username = st.text_input(
            "Choose Username",
            placeholder="Pick a unique username",
            key="reg_username"
        )
        new_password = st.text_input(
            "Create Password",
            type="password",
            placeholder="Create a secure password",
            key="reg_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="reg_confirm"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        register_btn = st.form_submit_button("🌟 Create Account", use_container_width=True)
        
        if register_btn:
            _handle_registration(new_username, new_password, confirm_password)

def _handle_login(username, password):
    """Handle user login"""
    if not username or not password:
        st.error("Please fill in all fields.")
        return
    
    with st.spinner("Signing you in..."):
        result = MindBuddyAPI.login(username, password)
    
    if result and result.get('token'):
        # Store authentication data
        st.session_state.user_token = result['token']
        st.session_state.user = result.get('user', {})
        st.session_state.username = username
        st.session_state.is_authenticated = True
        st.session_state.is_demo = False
        
        st.success("Welcome back! 🌟")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Invalid credentials. Please try again.")

def _handle_demo_login():
    """Handle demo mode login"""
    st.session_state.username = "demo_user"
    st.session_state.user = {"name": "Demo User", "id": "demo"}
    st.session_state.is_authenticated = True
    st.session_state.is_demo = True
    st.session_state.user_token = None  # No token for demo
    
    st.success("Welcome to Demo Mode! 🎉")
    time.sleep(1)
    st.rerun()

def _handle_registration(new_username, new_password, confirm_password):
    """Handle user registration"""
    if not new_username or not new_password or not confirm_password:
        st.error("Please fill in all fields.")
        return
    
    if new_password != confirm_password:
        st.error("Passwords don't match!")
        return
    
    with st.spinner("Creating your account..."):
        result = MindBuddyAPI.register(new_username, new_password)
    
    if result and result.get('token'):
        # Store authentication data
        st.session_state.user_token = result['token']
        st.session_state.user = result.get('user', {})
        st.session_state.username = new_username
        st.session_state.is_authenticated = True
        st.session_state.is_demo = False
        
        st.success("Account created successfully! Welcome to MindBuddy! 🎉")
        time.sleep(2)
        st.rerun()
    else:
        st.error("Registration failed. Username might already exist.")

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('is_authenticated', False)

def is_demo_mode():
    """Check if user is in demo mode"""
    return st.session_state.get('is_demo', False)

def get_auth_headers():
    """Get authentication headers for API requests"""
    if 'user_token' in st.session_state and st.session_state.user_token:
        return {'Authorization': f'Token {st.session_state.user_token}'}
    return {}

def get_current_user():
    """Get current user information"""
    return st.session_state.get('user', {})

def logout_user():
    """Logout current user"""
    if not is_demo_mode():
        MindBuddyAPI.logout()
    else:
        _clear_session()

def _clear_session():
    """Clear all session data"""
    keys_to_clear = [
        'user_token', 'user', 'username', 
        'is_authenticated', 'is_demo'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Additional utility functions for main app integration
def require_auth(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            auth_interface()
            return
        return func(*args, **kwargs)
    return wrapper

def show_logout_option():
    """Show logout button in sidebar or main area"""
    if is_authenticated():
        col1, col2 = st.columns([4, 1])
        with col1:
            if is_demo_mode():
                st.info("You're in Demo Mode")
            else:
                user = get_current_user()
                st.write(f"Welcome, {user.get('name', st.session_state.username)}!")
        
        with col2:
            if st.button("Logout", key="logout_btn"):
                logout_user()
                st.rerun()