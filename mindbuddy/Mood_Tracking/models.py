from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import date, datetime, timedelta

class MoodEntry(models.Model):
    """Model to store daily mood entries"""
    MOOD_CHOICES = [
        (1, 'Very Bad'),
        (2, 'Bad'),
        (3, 'Okay'),
        (4, 'Good'),
        (5, 'Very Good'),
    ]
    
    ENERGY_LEVELS = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Moderate'),
        (4, 'High'),
        (5, 'Very High'),
    ]
    
    ANXIETY_LEVELS = [
        (1, 'None'),
        (2, 'Mild'),
        (3, 'Moderate'),
        (4, 'High'),
        (5, 'Severe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    date = models.DateField(default=date.today)
    
    # Main mood rating (1-5 scale)
    mood_rating = models.IntegerField(
        choices=MOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Additional metrics
    energy_level = models.IntegerField(
        choices=ENERGY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    anxiety_level = models.IntegerField(
        choices=ANXIETY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Optional notes
    notes = models.TextField(blank=True, max_length=500)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']  # One entry per user per day
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_mood_rating_display()}"

class MoodStreak(models.Model):
    """Model to track mood logging streaks"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mood_streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_check_in = models.DateField(null=True, blank=True)
    total_entries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Current: {self.current_streak}, Best: {self.longest_streak}"

class MoodInsight(models.Model):
    """Model to store mood insights and patterns"""
    INSIGHT_TYPES = [
        ('weekly_average', 'Weekly Average'),
        ('monthly_trend', 'Monthly Trend'),
        ('pattern_detected', 'Pattern Detected'),
        ('milestone', 'Milestone Achieved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField(default=dict)  # Store insight data/metrics
    date_generated = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_generated']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"