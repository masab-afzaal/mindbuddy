from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import ChatInputSerializer, ConversationSerializer, MessageSerializer
from .services import GroqService, MemoryService

class ChatAPIView(APIView):
    """
    Main chat endpoint for receiving text input and returning Groq responses
    """
    # Remove authentication requirement for testing - change to IsAuthenticated for production
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.groq_service = GroqService()
            self.memory_service = MemoryService()
        except ImproperlyConfigured as e:
            self.groq_service = None
            self.config_error = str(e)
    
    def post(self, request):
        """Handle chat messages (text only)"""
        
        # Check if services are properly configured
        if not self.groq_service:
            return Response({
                'error': 'Configuration Error',
                'message': getattr(self, 'config_error', 'Groq service not properly configured')
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = ChatInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # For testing without authentication, use first user or create anonymous user
        if request.user.is_authenticated:
            user = request.user
        else:
            # Create or get a test user for unauthenticated requests
            user, created = User.objects.get_or_create(
                username='anonymous_user',
                defaults={
                    'email': 'anonymous@test.com',
                    'first_name': 'Anonymous',
                    'last_name': 'User'
                }
            )
        
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return Response(
                {'error': 'Message content cannot be empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation
        conversation = self._get_or_create_conversation(
            data.get('conversation_id'), user
        )
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            content=user_message,
            sender_type='user'
        )
        
        # Get conversation context and memory
        conversation_context = list(conversation.messages.all().order_by('-timestamp')[:20])
        conversation_context.reverse()  # oldest first
        memory = self.memory_service.get_or_create_memory(conversation)
        
        # Generate Groq response
        groq_response = self.groq_service.get_therapeutic_response(
            user_message=user_message,
            conversation_context=conversation_context,
            user_memory=memory.user_profile
        )
        
        # Save Groq response
        assistant_msg = Message.objects.create(
            conversation=conversation,
            content=groq_response['content'],
            sender_type='assistant',
            model_used=groq_response.get('model'),
            response_time=groq_response.get('response_time'),
            token_usage=groq_response.get('token_usage')
        )
        
        # Update memory
        self.memory_service.update_memory(
            conversation, user_message, groq_response['content']
        )
        
        # Update conversation timestamp
        conversation.save()
        
        return Response({
            'conversation_id': str(conversation.id),
            'user_message': MessageSerializer(user_msg).data,
            'assistant_response': MessageSerializer(assistant_msg).data,
            'status': 'success'
        }, status=status.HTTP_200_OK)
    
    def _get_or_create_conversation(self, conversation_id, user):
        """Get existing conversation or create new one"""
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                pass
        
        return Conversation.objects.create(user=user, title="New Conversation")

class ConversationListView(APIView):
    """List user's conversations"""
    permission_classes = [AllowAny]  # Remove auth for testing
    
    def get(self, request):
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({'conversations': []})
        
        conversations = Conversation.objects.filter(
            user=user, is_active=True
        )
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class ConversationDetailView(APIView):
    """Get conversation details with messages"""
    permission_classes = [AllowAny]  # Remove auth for testing
    
    def get(self, request, conversation_id):
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({'error': 'No conversations found'}, status=404)
        
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=user
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

class ConversationListView(APIView):
    """List user's conversations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        conversations = Conversation.objects.filter(
            user=request.user, is_active=True
        )
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class ConversationDetailView(APIView):
    """Get conversation details with messages"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=request.user
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
