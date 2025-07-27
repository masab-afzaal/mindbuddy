from django.contrib import admin
from .models import QuizTopic, Quiz, QuizResult, QuizHistory

@admin.register(QuizTopic)
class QuizTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'length', 'user', 'created_at']
    list_filter = ['length', 'topic', 'created_at']
    search_fields = ['topic__name', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'user', 'completed_at', 'liked']
    list_filter = ['liked', 'completed_at', 'quiz__topic']
    search_fields = ['quiz__topic__name', 'user__username']
    ordering = ['-completed_at']
    readonly_fields = ['completed_at']

@admin.register(QuizHistory)
class QuizHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'user', 'date']
    list_filter = ['topic', 'date']
    search_fields = ['topic__name', 'user__username']
    ordering = ['-date']
    readonly_fields = ['date']