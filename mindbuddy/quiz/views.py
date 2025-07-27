from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import QuizTopic, Quiz, QuizResult, QuizHistory
from .serializers import QuizTopicSerializer, QuizSerializer, QuizResultSerializer, QuizHistorySerializer
from .services import QuizService

quiz_service = QuizService()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz_topics(request):
    """Get all available quiz topics"""
    topics = QuizTopic.objects.all()
    serializer = QuizTopicSerializer(topics, many=True)
    
    # Add default topics if none exist
    default_topics = [
        "Managing Daily Stress", "Improving Sleep Quality", "Building Mindfulness Habits", 
        "Work-Life Balance", "Practicing Self-Compassion", "Overcoming Procrastination",
        "Fostering Positive Thinking", "Understanding My Emotions", "Building Healthy Relationships"
    ]
    
    if not topics.exists():
        for topic_name in default_topics:
            QuizTopic.objects.get_or_create(name=topic_name)
        
        topics = QuizTopic.objects.all()
        serializer = QuizTopicSerializer(topics, many=True)
    
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_quiz(request):
    """Create a new quiz with AI-generated questions"""
    try:
        data = request.data
        topic_name = data.get('topic')
        length = int(data.get('length', 5))
        
        if not topic_name:
            return Response(
                {'error': 'Topic is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if length not in [3, 5, 8]:
            return Response(
                {'error': 'Length must be 3, 5, or 8'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user if request.user.is_authenticated else None
        quiz = quiz_service.create_quiz(topic_name, length, user)
        
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to create quiz'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz(request, quiz_id):
    """Get a specific quiz by ID"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_quiz(request, quiz_id):
    """Submit quiz answers and get insights"""
    try:
        data = request.data
        answers = data.get('answers', [])
        
        if not answers:
            return Response(
                {'error': 'Answers are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user if request.user.is_authenticated else None
        result = quiz_service.submit_quiz_answers(quiz_id, answers, user)
        
        serializer = QuizResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to submit quiz'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def regenerate_insights(request, result_id):
    """Regenerate insights for a quiz result"""
    try:
        user = request.user if request.user.is_authenticated else None
        result = quiz_service.regenerate_insights(result_id, user)
        
        serializer = QuizResultSerializer(result)
        return Response(serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to regenerate insights'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def like_insight(request, result_id):
    """Mark an insight as liked"""
    try:
        user = request.user if request.user.is_authenticated else None
        result = quiz_service.like_insight(result_id, user)
        
        return Response({'message': 'Insight liked successfully'})
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def dislike_insight(request, result_id):
    """Mark an insight as disliked"""
    try:
        user = request.user if request.user.is_authenticated else None
        result = quiz_service.dislike_insight(result_id, user)
        
        return Response({'message': 'Insight disliked successfully'})
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz_history(request):
    """Get user's quiz history"""
    user = request.user if request.user.is_authenticated else None
    history = quiz_service.get_user_quiz_history(user)
    serializer = QuizHistorySerializer(history, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz_results(request):
    """Get user's quiz results"""
    user = request.user if request.user.is_authenticated else None
    results = QuizResult.objects.filter(user=user).order_by('-completed_at')
    serializer = QuizResultSerializer(results, many=True)
    return Response(serializer.data)