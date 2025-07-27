"""
MindBuddy Chat Interface Module
Handles the chat functionality with the AI buddy
"""

import streamlit as st
import random
from datetime import datetime
from api_client import MindBuddyAPI

def chat_interface(user_token):
    """Main chat interface"""
    st.markdown("### 💬 Chat with MindBuddy")
    st.markdown("*I'm here to listen and support you on your wellness journey* 🌟")
    
    # Load chat history if empty
    if not st.session_state.chat_messages:
        _load_chat_history(user_token)
    
    # Chat interface
    st.markdown('<div class="chat-interface">', unsafe_allow_html=True)
    
    # Messages area
    _display_chat_messages()
    
    # Input area
    _chat_input_form(user_token)
    
    st.markdown('</div>', unsafe_allow_html=True)

def _load_chat_history(user_token):
    """Load chat history from API or initialize with welcome message"""
    if not st.session_state.is_demo:
        history_result = MindBuddyAPI.get_chat_history(token=user_token)
        if history_result and history_result.get('messages'):
            st.session_state.chat_messages = history_result['messages']
    
    # Add welcome message if no history
    if not st.session_state.chat_messages:
        welcome_msg = f"Hello {st.session_state.username}! I'm MindBuddy 🌸 I'm here to listen and support you. How are you feeling today?"
        st.session_state.chat_messages.append({
            "role": "assistant", 
            "content": welcome_msg,
            "timestamp": datetime.now().strftime("%H:%M")
        })

def _display_chat_messages():
    """Display all chat messages"""
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    for message in st.session_state.chat_messages:
        _display_message(message)
    st.markdown('</div>', unsafe_allow_html=True)

def _display_message(message):
    """Display a single chat message"""
    if message["role"] == "user":
        st.markdown(f'''
        <div class="message-bubble user-bubble">
            {message["content"]}
            <div style="font-size: 0.75rem; opacity: 0.7; text-align: right; margin-top: 0.5rem;">
                {message.get("timestamp", "")}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="message-bubble assistant-bubble">
            {message["content"]}
            <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 0.5rem;">
                {message.get("timestamp", "")}
            </div>
        </div>
        ''', unsafe_allow_html=True)

def _chat_input_form(user_token):
    """Chat input form with send and voice buttons"""
    with st.form("chat_form", clear_on_submit=True):
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.8, 6, 0.8])
        
        with col1:
            voice_btn = st.form_submit_button("🎤", help="Record voice message")
        
        with col2:
            user_input = st.text_area(
                "",
                placeholder="Share what's on your mind... 💭",
                height=60,
                key="chat_input",
                label_visibility="collapsed"
            )
        
        with col3:
            send_btn = st.form_submit_button("🚀", help="Send message")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if voice_btn:
            st.info("🎙️ Voice recording feature coming soon! For now, please use text input.")
        
        if send_btn and user_input.strip():
            _handle_message_send(user_input.strip(), user_token)
        elif send_btn and not user_input.strip():
            st.warning("Please enter a message before sending! 💌")

def _handle_message_send(user_input, user_token):
    """Handle sending a message and getting AI response"""
    # Add user message
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Get AI response
    with st.spinner("MindBuddy is thinking... 🤔"):
        if st.session_state.is_demo:
            ai_response = _get_demo_response()
        else:
            response = MindBuddyAPI.chat_with_buddy(user_input, token=user_token)
            ai_response = response.get('assistant_response', {}).get('content') if response else "I'm sorry, I'm having trouble connecting right now. Please try again."
    
    # Add AI response
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    st.rerun()

def _get_demo_response():
    """Get a demo response for demo mode"""
    demo_responses = [
        "Thank you for sharing that with me. I can hear that you're going through something important. Can you tell me more about how this is affecting you emotionally?",
        "I appreciate you opening up to me. It sounds like you're dealing with a lot right now. What would feel most supportive for you in this moment?",
        "Your feelings are completely valid. It's okay to feel overwhelmed sometimes. What usually helps you when you're feeling this way?",
        "I'm here to listen without judgment. It takes courage to share what you're experiencing. How long have you been feeling this way?",
        "That sounds really challenging. I want you to know that what you're feeling is important and valid. How are you taking care of yourself during this time?",
        "I hear you, and I'm grateful you feel comfortable sharing this with me. Sometimes talking through our thoughts can help us process them better. What's weighing on your mind the most?",
        "It takes strength to reach out when we're struggling. I'm here to support you through this. What would be most helpful for you right now?",
        "Thank you for trusting me with your feelings. Everyone deserves to be heard and supported. What's one small thing that might bring you a little comfort today?"
    ]
    return random.choice(demo_responses)