from django.contrib import admin
from .models import MoodEntry, MoodStreak, MoodInsight

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'mood_rating', 'energy_level', 'anxiety_level', 'created_at']
    list_filter = ['mood_rating', 'date', 'energy_level', 'anxiety_level']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(MoodStreak)
class MoodStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_entries', 'last_check_in']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(MoodInsight)
class MoodInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'title', 'date_generated', 'is_read']
    list_filter = ['insight_type', 'is_read', 'date_generated']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['id', 'date_generated']
