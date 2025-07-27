import os
import requests
import json
from datetime import datetime
from django.conf import settings
from .models import QuizTopic, Quiz, QuizResult, QuizHistory

class AIQuizService:
    def __init__(self):
        self.api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in Django settings")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_quiz_questions(self, topic, num_questions):
        """Generate quiz questions using AI"""
        prompt = f'''You are a wellness assistant. Create a {num_questions}-question multiple-choice quiz about "{topic}". 
        You MUST return the output as a single, valid JSON array of objects with this exact format:
        [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"]
            }}
        ]
        Make sure each question is thoughtful and relevant to wellness and mental health.'''
        
        try:
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "system", "content": prompt}],
                "max_tokens": 2048,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            response_data = json.loads(response.json()['choices'][0]['message']['content'])
            
            # Handle different response formats
            if isinstance(response_data, dict):
                for value in response_data.values():
                    if isinstance(value, list):
                        return value
            elif isinstance(response_data, list):
                return response_data
                
            return None
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None
    
    def generate_insights(self, topic, current_results, previous_results=None, disliked_text=None):
        """Generate personalized insights based on quiz results"""
        current_results_str = "\n".join([
            f"- {item['question']}: {item['answer']}" 
            for item in current_results
        ])
        
        if disliked_text:
            feedback_context = f"""The user DISLIKED the previous response: '{disliked_text}'. 
            Please generate a NEW insight with a different tone and approach. 
            The user's current answers are:\n{current_results_str}"""
        else:
            if previous_results and 'results_data' in previous_results:
                previous_results_str = "\n".join([
                    f"- {item['question']}: {item['answer']}" 
                    for item in previous_results['results_data']
                ])
                feedback_context = f"""The user took this quiz before on {previous_results['date']}. 
                Please compare their new results to the old ones.
                Previous answers:\n{previous_results_str}\n\nCurrent answers:\n{current_results_str}"""
            else:
                feedback_context = f"This is the user's first time taking this quiz. Their answers are:\n{current_results_str}"
        
        system_prompt = f"""You are an empathetic wellness coach. A user has completed a quiz about "{topic}". 
        Your tone must be warm and kind. NEVER use clinical language.
        
        USER CONTEXT: {feedback_context}
        
        FORMATTING RULES: Structure your response using Markdown. Start with a warm opening. 
        Follow it with the bolded heading **Here are a few gentle suggestions:** and list each 
        suggestion as a separate bullet point (`*`).
        """
        
        try:
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "system", "content": system_prompt}],
                "max_tokens": 1024
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return "Sorry, I had trouble generating insights. Please try again later."

class QuizService:
    def __init__(self):
        self.ai_service = AIQuizService()
    
    def get_or_create_topic(self, topic_name):
        """Get or create a quiz topic"""
        topic, created = QuizTopic.objects.get_or_create(
            name=topic_name.strip()
        )
        return topic
    
    def create_quiz(self, topic_name, length, user=None):
        """Create a new quiz with AI-generated questions"""
        topic = self.get_or_create_topic(topic_name)
        
        # Generate questions using AI
        questions = self.ai_service.generate_quiz_questions(topic_name, length)
        
        if not questions or len(questions) != length:
            raise ValueError("Failed to generate quiz questions")
        
        quiz = Quiz.objects.create(
            user=user,
            topic=topic,
            length=length,
            questions_data=questions
        )
        
        return quiz
    
    def submit_quiz_answers(self, quiz_id, answers, user=None):
        """Submit quiz answers and generate insights"""
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")
        
        # Prepare results data
        results_data = []
        for i, question in enumerate(quiz.questions_data):
            if i < len(answers):
                results_data.append({
                    "question": question['question'],
                    "answer": answers[i]
                })
        
        # Get previous results for comparison
        previous_results = self.get_previous_quiz_history(quiz.topic.name, user)
        
        # Generate insights
        insights = self.ai_service.generate_insights(
            quiz.topic.name, 
            results_data, 
            previous_results
        )
        
        # Save quiz result
        quiz_result = QuizResult.objects.create(
            user=user,
            quiz=quiz,
            answers_data=results_data,
            insights=insights
        )
        
        # Save to history
        self.save_quiz_history(quiz.topic, results_data, user)
        
        return quiz_result
    
    def regenerate_insights(self, result_id, user=None):
        """Regenerate insights for a quiz result (when user dislikes previous insights)"""
        try:
            result = QuizResult.objects.get(id=result_id, user=user)
        except QuizResult.DoesNotExist:
            raise ValueError("Quiz result not found")
        
        # Get previous results for comparison
        previous_results = self.get_previous_quiz_history(result.quiz.topic.name, user)
        
        # Generate new insights with disliked context
        new_insights = self.ai_service.generate_insights(
            result.quiz.topic.name,
            result.answers_data,
            previous_results,
            disliked_text=result.insights
        )
        
        # Update insights
        result.insights = new_insights
        result.liked = None  # Reset feedback
        result.save()
        
        return result
    
    def get_previous_quiz_history(self, topic_name, user=None):
        """Get previous quiz history for a topic"""
        try:
            topic = QuizTopic.objects.get(name=topic_name)
            history = QuizHistory.objects.filter(
                topic=topic, 
                user=user
            ).order_by('-date').first()
            
            if history:
                return {
                    'date': history.date.strftime("%B %d, %Y"),
                    'results_data': history.results_data
                }
        except QuizTopic.DoesNotExist:
            pass
        
        return None
    
    def save_quiz_history(self, topic, results_data, user=None):
        """Save quiz results to history"""
        QuizHistory.objects.update_or_create(
            user=user,
            topic=topic,
            defaults={
                'results_data': results_data
            }
        )
    
    def get_user_quiz_history(self, user=None):
        """Get all quiz history for a user"""
        return QuizHistory.objects.filter(user=user).order_by('-date')
    
    def like_insight(self, result_id, user=None):
        """Mark insight as liked"""
        try:
            result = QuizResult.objects.get(id=result_id, user=user)
            result.liked = True
            result.save()
            return result
        except QuizResult.DoesNotExist:
            raise ValueError("Quiz result not found")
    
    def dislike_insight(self, result_id, user=None):
        """Mark insight as disliked"""
        try:
            result = QuizResult.objects.get(id=result_id, user=user)
            result.liked = False
            result.save()
            return result
        except QuizResult.DoesNotExist:
            raise ValueError("Quiz result not found")