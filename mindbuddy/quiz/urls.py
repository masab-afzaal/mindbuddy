from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Quiz topics
    path('topics/', views.get_quiz_topics, name='get_topics'),
    
    # Quiz management
    path('create/', views.create_quiz, name='create_quiz'),
    path('<int:quiz_id>/', views.get_quiz, name='get_quiz'),
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # Results and insights
    path('results/<int:result_id>/regenerate/', views.regenerate_insights, name='regenerate_insights'),
    path('results/<int:result_id>/like/', views.like_insight, name='like_insight'),
    path('results/<int:result_id>/dislike/', views.dislike_insight, name='dislike_insight'),
    
    # History
    path('history/', views.get_quiz_history, name='get_history'),
    path('results/', views.get_quiz_results, name='get_results'),
]