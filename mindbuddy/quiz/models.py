from django.db import models
from django.conf import settings
import json

class QuizTopic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    LENGTH_CHOICES = [
        (3, '3 Questions'),
        (5, '5 Questions'),
        (8, '8 Questions'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(QuizTopic, on_delete=models.CASCADE)
    length = models.IntegerField(choices=LENGTH_CHOICES)
    questions_data = models.JSONField()  # Store the generated questions
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quiz: {self.topic.name} ({self.length} questions)"

class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answers_data = models.JSONField()  # Store user answers
    insights = models.TextField(blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    liked = models.BooleanField(null=True, blank=True)  # True for like, False for dislike, None for no feedback
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"Result for {self.quiz.topic.name} - {self.completed_at.strftime('%Y-%m-%d')}"
    
    def get_previous_results(self):
        """Get previous results for the same topic by the same user"""
        return QuizResult.objects.filter(
            user=self.user,
            quiz__topic=self.quiz.topic,
            completed_at__lt=self.completed_at
        ).order_by('-completed_at')

class QuizHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(QuizTopic, on_delete=models.CASCADE)
    results_data = models.JSONField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'topic', 'date']
    
    def __str__(self):
        return f"History: {self.topic.name} - {self.date.strftime('%Y-%m-%d')}"