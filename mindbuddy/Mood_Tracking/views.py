from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import date, timedelta
from .models import MoodEntry, MoodStreak, MoodInsight
from .serializers import (
    MoodEntrySerializer, MoodEntryCreateSerializer, 
    MoodStreakSerializer, MoodInsightSerializer, MoodHistorySerializer
)
from .services import MoodService

class MoodLogView(APIView):
    """
    API endpoint to log daily mood
    POST /mood/ - Log mood for a specific date
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def post(self, request):
        """Log mood entry"""
        
        # Handle unauthenticated users (for testing)
        if request.user.is_authenticated:
            user = request.user
        else:
            user, created = User.objects.get_or_create(
                username='anonymous_user',
                defaults={
                    'email': 'anonymous@test.com',
                    'first_name': 'Anonymous',
                    'last_name': 'User'
                }
            )
        
        serializer = MoodEntryCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create mood entry
            mood_entry = serializer.save(user=user)
            
            # Update streak
            streak = MoodService.update_streak(user, mood_entry.date)
            
            # Generate weekly insight if it's been 7 days
            if streak.total_entries % 7 == 0:
                MoodService.generate_weekly_insight(user)
            
            return Response({
                'mood_entry': MoodEntrySerializer(mood_entry).data,
                'streak': MoodStreakSerializer(streak).data,
                'status': 'success'
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            # Entry already exists for this date
            existing_entry = MoodEntry.objects.get(user=user, date=serializer.validated_data['date'])
            return Response({
                'error': 'Mood already logged for this date',
                'existing_entry': MoodEntrySerializer(existing_entry).data
            }, status=status.HTTP_400_BAD_REQUEST)

class MoodHistoryView(APIView):
    """
    API endpoint to get mood history for charts
    GET /mood/history/ - Returns mood chart data
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def get(self, request):
        """Get mood history data"""
        
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({'chart_data': [], 'message': 'No mood data found'})
        
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        days = min(days, 365)  # Limit to 1 year max
        
        # Get chart data
        chart_data = MoodService.get_mood_chart_data(user, days)
        
        # Calculate statistics
        entries_with_data = [entry for entry in chart_data if entry['has_entry']]
        
        stats = {}
        if entries_with_data:
            mood_ratings = [entry['mood_rating'] for entry in entries_with_data]
            stats = {
                'total_entries': len(entries_with_data),
                'average_mood': sum(mood_ratings) / len(mood_ratings),
                'best_mood': max(mood_ratings),
                'worst_mood': min(mood_ratings),
                'tracking_percentage': (len(entries_with_data) / days) * 100
            }
        
        return Response({
            'chart_data': chart_data,
            'statistics': stats,
            'period_days': days
        })

class MoodStreakView(APIView):
    """
    API endpoint to get current mood streak information
    GET /mood/streak/ - Returns streak data
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def get(self, request):
        """Get mood streak information"""
        
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({
                    'current_streak': 0,
                    'longest_streak': 0,
                    'total_entries': 0,
                    'last_check_in': None
                })
        
        try:
            streak = MoodStreak.objects.get(user=user)
            return Response(MoodStreakSerializer(streak).data)
        except MoodStreak.DoesNotExist:
            return Response({
                'current_streak': 0,
                'longest_streak': 0,
                'total_entries': 0,
                'last_check_in': None
            })

class MoodInsightsView(APIView):
    """
    API endpoint to get mood insights
    GET /mood/insights/ - Returns generated insights
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def get(self, request):
        """Get mood insights"""
        
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({'insights': []})
        
        insights = MoodInsight.objects.filter(user=user)[:10]  # Latest 10 insights
        
        return Response({
            'insights': MoodInsightSerializer(insights, many=True).data
        })

class TodayMoodView(APIView):
    """
    API endpoint to get/update today's mood
    GET /mood/today/ - Get today's mood entry
    PUT /mood/today/ - Update today's mood entry
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def get(self, request):
        """Get today's mood entry"""
        
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            try:
                user = User.objects.get(username='anonymous_user')
            except User.DoesNotExist:
                return Response({'today_mood': None, 'has_logged_today': False})
        
        try:
            today_entry = MoodEntry.objects.get(user=user, date=date.today())
            return Response({
                'today_mood': MoodEntrySerializer(today_entry).data,
                'has_logged_today': True
            })
        except MoodEntry.DoesNotExist:
            return Response({'today_mood': None, 'has_logged_today': False})
    
    def put(self, request):
        """Update today's mood entry"""
        
        # Handle unauthenticated users
        if request.user.is_authenticated:
            user = request.user
        else:
            user, created = User.objects.get_or_create(
                username='anonymous_user',
                defaults={
                    'email': 'anonymous@test.com',
                    'first_name': 'Anonymous',
                    'last_name': 'User'
                }
            )
        
        try:
            today_entry = MoodEntry.objects.get(user=user, date=date.today())
            serializer = MoodEntryCreateSerializer(today_entry, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'mood_entry': MoodEntrySerializer(today_entry).data,
                    'status': 'updated'
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except MoodEntry.DoesNotExist:
            return Response({'error': 'No mood entry found for today'}, status=status.HTTP_404_NOT_FOUND)

