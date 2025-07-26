from django.contrib import admin
from .models import Conversation, Message, ConversationMemory

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender_type', 'timestamp']
    list_filter = ['sender_type', 'timestamp']
    search_fields = ['content', 'conversation__user__username']
    readonly_fields = ['id', 'timestamp']

@admin.register(ConversationMemory)
class ConversationMemoryAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'last_updated']
    readonly_fields = ['conversation', 'last_updated']