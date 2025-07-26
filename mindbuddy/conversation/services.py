from groq import Groq
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import time
import json
from .models import Conversation, Message, ConversationMemory

class GroqService:
    """Service for handling Groq API calls"""
    
    def __init__(self):
        # Check if Groq API key is configured
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            raise ImproperlyConfigured(
                "GROQ_API_KEY is not set in Django settings. "
                "Please add GROQ_API_KEY = 'your-api-key-here' to your settings.py"
            )
        
        self.client = Groq(api_key=api_key)
        self.model = getattr(settings, 'GROQ_MODEL', "llama3-8b-8192")
    
    def get_therapeutic_response(self, user_message, conversation_context=None, user_memory=None):
        """Generate therapeutic response using Groq"""
        
        # Build system prompt for therapeutic context
        system_prompt = self._build_therapeutic_prompt(user_memory)
        
        # Prepare messages for API call
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation context if available
        if conversation_context:
            for msg in conversation_context[-10:]:  # Last 10 messages for context
                role = "user" if msg.sender_type == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                stop=None,
            )
            
            response_time = time.time() - start_time
            
            return {
                'content': response.choices[0].message.content,
                'model': self.model,
                'response_time': response_time,
                'token_usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                } if response.usage else None
            }
            
        except Exception as e:
            return {
                'content': "I'm sorry, I'm having trouble processing your message right now. Please try again.",
                'error': str(e),
                'model': self.model,
                'response_time': time.time() - start_time
            }
    
    def _build_therapeutic_prompt(self, user_memory=None):
        """Build therapeutic system prompt"""
        base_prompt = """You are MindBuddy, a compassionate AI therapeutic assistant. Your role is to:

1. Provide empathetic, supportive responses
2. Help users explore their thoughts and feelings
3. Offer coping strategies and mindfulness techniques
4. Encourage self-reflection and personal growth
5. Always maintain professional boundaries
6. Suggest professional help when appropriate

Guidelines:
- Be warm, understanding, and non-judgmental
- Ask thoughtful follow-up questions
- Validate emotions while encouraging healthy perspectives
- Keep responses concise but meaningful
- Never diagnose or provide medical advice
- Focus on the user's strengths and resilience"""

        if user_memory:
            memory_context = f"\n\nUser Context:\n{json.dumps(user_memory, indent=2)}"
            return base_prompt + memory_context
        
        return base_prompt

class MemoryService:
    """Service for managing conversation memory"""
    
    def get_or_create_memory(self, conversation):
        """Get or create memory for conversation"""
        memory, created = ConversationMemory.objects.get_or_create(
            conversation=conversation,
            defaults={
                'user_profile': {},
                'conversation_summary': '',
                'key_insights': [],
                'therapeutic_goals': []
            }
        )
        return memory
    
    def update_memory(self, conversation, user_message, gpt_response):
        """Update conversation memory with new insights"""
        memory = self.get_or_create_memory(conversation)
        
        # Extract key information (simplified - could use NLP here)
        if any(word in user_message.lower() for word in ['anxious', 'anxiety', 'worried']):
            if 'anxiety' not in memory.key_insights:
                memory.key_insights.append('anxiety')
        
        if any(word in user_message.lower() for word in ['sad', 'depressed', 'down']):
            if 'depression' not in memory.key_insights:
                memory.key_insights.append('depression')
        
        # Update session notes
        memory.session_notes += f"\nUser: {user_message[:100]}...\nAssistant: {gpt_response[:100]}...\n"
        memory.save()
        
        return memory