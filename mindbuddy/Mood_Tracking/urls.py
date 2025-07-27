from django.urls import path
from .views import (
    MoodLogView, MoodHistoryView, MoodStreakView, 
    MoodInsightsView, TodayMoodView
)

app_name = 'mood'

urlpatterns = [
    path('', MoodLogView.as_view(), name='mood-log'),
    path('history/', MoodHistoryView.as_view(), name='mood-history'),
    path('streak/', MoodStreakView.as_view(), name='mood-streak'),
    path('insights/', MoodInsightsView.as_view(), name='mood-insights'),
    path('today/', TodayMoodView.as_view(), name='today-mood'),
]

