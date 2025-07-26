from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import MoodEntry, MoodStreak, MoodInsight
import json

class MoodService:
    """Service for mood-related business logic"""
    
    @staticmethod
    def update_streak(user, entry_date):
        """Update user's mood streak after logging an entry"""
        streak, created = MoodStreak.objects.get_or_create(
            user=user,
            defaults={
                'current_streak': 0,
                'longest_streak': 0,
                'total_entries': 0
            }
        )
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Update total entries
        streak.total_entries = MoodEntry.objects.filter(user=user).count()
        
        if entry_date == today:
            # Logging for today
            if streak.last_check_in == yesterday:
                # Continuing streak
                streak.current_streak += 1
            elif streak.last_check_in == today:
                # Already logged today, no streak change
                pass
            else:
                # Starting new streak
                streak.current_streak = 1
            
            streak.last_check_in = today
            
        elif entry_date == yesterday and streak.last_check_in != yesterday:
            # Logging for yesterday
            if streak.last_check_in == entry_date - timedelta(days=1):
                streak.current_streak += 1
            else:
                streak.current_streak = 1
            
            streak.last_check_in = entry_date
        
        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
            
            # Generate milestone insight
            if streak.current_streak in [7, 30, 100]:
                MoodInsight.objects.create(
                    user=user,
                    insight_type='milestone',
                    title=f"{streak.current_streak} Day Streak!",
                    description=f"Congratulations! You've maintained a {streak.current_streak}-day mood logging streak.",
                    data={'streak_length': streak.current_streak}
                )
        
        streak.save()
        return streak
    
    @staticmethod
    def generate_weekly_insight(user):
        """Generate weekly mood insights"""
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        entries = MoodEntry.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        if entries.exists():
            avg_mood = entries.aggregate(Avg('mood_rating'))['mood_rating__avg']
            avg_energy = entries.aggregate(Avg('energy_level'))['energy_level__avg'] or 0
            avg_anxiety = entries.aggregate(Avg('anxiety_level'))['anxiety_level__avg'] or 0
            
            # Create insight
            MoodInsight.objects.create(
                user=user,
                insight_type='weekly_average',
                title="Weekly Mood Summary",
                description=f"Your average mood this week was {avg_mood:.1f}/5. Keep tracking to see your patterns!",
                data={
                    'avg_mood': round(avg_mood, 2),
                    'avg_energy': round(avg_energy, 2),
                    'avg_anxiety': round(avg_anxiety, 2),
                    'entries_count': entries.count()
                }
            )
    
    @staticmethod
    def get_mood_chart_data(user, days=30):
        """Get mood chart data for specified number of days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get all entries in range
        entries = MoodEntry.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Create complete date range with mood data
        chart_data = []
        current_date = start_date
        
        while current_date <= end_date:
            entry = entries.filter(date=current_date).first()
            
            if entry:
                chart_data.append({
                    'date': current_date,
                    'mood_rating': entry.mood_rating,
                    'energy_level': entry.energy_level or 0,
                    'anxiety_level': entry.anxiety_level or 0,
                    'notes': entry.notes,
                    'has_entry': True
                })
            else:
                chart_data.append({
                    'date': current_date,
                    'mood_rating': None,
                    'energy_level': None,
                    'anxiety_level': None,
                    'notes': '',
                    'has_entry': False
                })
            
            current_date += timedelta(days=1)
        
        return chart_data
