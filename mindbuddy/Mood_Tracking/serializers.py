from rest_framework import serializers
from django.utils import timezone
from datetime import date, timedelta
from .models import MoodEntry, MoodStreak, MoodInsight

class MoodEntrySerializer(serializers.ModelSerializer):
    mood_display = serializers.CharField(source='get_mood_rating_display', read_only=True)
    energy_display = serializers.CharField(source='get_energy_level_display', read_only=True)
    anxiety_display = serializers.CharField(source='get_anxiety_level_display', read_only=True)
    
    class Meta:
        model = MoodEntry
        fields = [
            'id', 'date', 'mood_rating', 'mood_display', 
            'energy_level', 'energy_display', 'anxiety_level', 'anxiety_display',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class MoodEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodEntry
        fields = ['date', 'mood_rating', 'energy_level', 'anxiety_level', 'notes']
    
    def validate_date(self, value):
        # Don't allow future dates
        if value > date.today():
            raise serializers.ValidationError("Cannot log mood for future dates.")
        
        # Don't allow dates older than 7 days
        if value < date.today() - timedelta(days=7):
            raise serializers.ValidationError("Cannot log mood for dates older than 7 days.")
        
        return value

class MoodStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodStreak
        fields = ['current_streak', 'longest_streak', 'last_check_in', 'total_entries']

class MoodInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodInsight
        fields = ['id', 'insight_type', 'title', 'description', 'data', 'date_generated', 'is_read']

class MoodHistorySerializer(serializers.Serializer):
    """Serializer for mood history chart data"""
    date = serializers.DateField()
    mood_rating = serializers.IntegerField()
    energy_level = serializers.IntegerField()
    anxiety_level = serializers.IntegerField()
    notes = serializers.CharField()
