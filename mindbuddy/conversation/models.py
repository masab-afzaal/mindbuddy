from django.db import models
from django.conf import settings  # This will reference your custom User model
from django.utils import timezone
import uuid

class Conversation(models.Model):
    """Model to store conversation sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user.name}"  # Changed from username to name

class Message(models.Model):
    """Model to store individual messages in conversations"""
    SENDER_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # For Groq response metadata
    model_used = models.CharField(max_length=50, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    token_usage = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."

class ConversationMemory(models.Model):
    """Model to store conversation memory and context"""
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='memory')
    user_profile = models.JSONField(default=dict)  # Store user preferences, concerns, etc.
    conversation_summary = models.TextField(blank=True)
    key_insights = models.JSONField(default=list)  # Important therapeutic insights
    therapeutic_goals = models.JSONField(default=list)  # User's goals and progress
    session_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Memory for {self.conversation.id}"
