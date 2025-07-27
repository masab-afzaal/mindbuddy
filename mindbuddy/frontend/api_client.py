"""
MindBuddy API Client
Handles all communication with the backend API
"""

import requests

# Configuration
API_BASE_URL = "http://localhost:8000/api"

class MindBuddyAPI:
    """Enhanced API client for MindBuddy backend"""
    
    @staticmethod
    def login(username, password):
        """User login"""
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login/", json={
                "username": username,
                "password": password
            })
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def register(username, password):
        """User registration - removed email parameter"""
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register/", json={
                "username": username,
                "password": password
            })
            return response.json() if response.status_code in [200, 201] else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def log_mood(mood_data, token=None):
        """Log mood entry with authentication"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.post(f"{API_BASE_URL}/mood/", json=mood_data, headers=headers)
            return response.json() if response.status_code in [200, 201] else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_mood_history(days=30, token=None):
        """Get mood history with authentication"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{API_BASE_URL}/mood/history/?days={days}", headers=headers)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_streak_info(token=None):
        """Get streak information with authentication"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{API_BASE_URL}/mood/streak/", headers=headers)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_today_mood(token=None):
        """Get today's mood with authentication"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{API_BASE_URL}/mood/today/", headers=headers)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def chat_with_buddy(message, audio_data=None, token=None):
        """Enhanced chat with voice support"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            payload = {"message": message}
            
            # Add audio data if provided
            if audio_data:
                payload["audio_data"] = audio_data
                payload["has_audio"] = True
            
            response = requests.post(f"{API_BASE_URL}/chat/", json=payload, headers=headers)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_chat_history(limit=50, token=None):
        """Get chat history"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{API_BASE_URL}/chat/history/?limit={limit}", headers=headers)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None

# Utility functions for mood handling
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