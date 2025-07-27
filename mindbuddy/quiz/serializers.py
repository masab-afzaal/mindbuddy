from rest_framework import serializers
from .models import QuizTopic, Quiz, QuizResult, QuizHistory

class QuizTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizTopic
        fields = ['id', 'name', 'created_at']

class QuizSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'topic', 'topic_name', 'length', 'questions_data', 'created_at']

class QuizResultSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='quiz.topic.name', read_only=True)
    quiz_id = serializers.IntegerField(source='quiz.id', read_only=True)
    
    class Meta:
        model = QuizResult
        fields = ['id', 'quiz_id', 'topic_name', 'answers_data', 'insights', 'completed_at', 'liked']

class QuizHistorySerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = QuizHistory
        fields = ['id', 'topic', 'topic_name', 'results_data', 'date']