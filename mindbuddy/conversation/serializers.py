from rest_framework import serializers
from .models import Conversation, Message, ConversationMemory

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender_type', 'timestamp', 
                 'model_used', 'response_time']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 
                 'messages', 'message_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    conversation_id = serializers.UUIDField(required=False)