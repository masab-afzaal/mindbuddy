import streamlit as st
import requests
import json
from datetime import datetime

class QuizComponent:
    def __init__(self, api_base_url="http://localhost:8000/api/quiz"):
        self.api_base_url = api_base_url
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'quiz_data' not in st.session_state:
            st.session_state.quiz_data = None
        if 'quiz_answers' not in st.session_state:
            st.session_state.quiz_answers = {}
        if 'quiz_result' not in st.session_state:
            st.session_state.quiz_result = None
        if 'show_results' not in st.session_state:
            st.session_state.show_results = False
    
    def get_topics(self):
        """Fetch available quiz topics from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/topics/")
            if response.status_code == 200:
                topics = response.json()
                return [topic['name'] for topic in topics]
            else:
                st.error("Failed to fetch topics")
                return []
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")
            return []
    
    def create_quiz(self, topic, length):
        """Create a new quiz"""
        try:
            payload = {
                'topic': topic,
                'length': length
            }
            response = requests.post(f"{self.api_base_url}/create/", json=payload)
            
            if response.status_code == 201:
                return response.json()
            else:
                error_data = response.json()
                st.error(f"Failed to create quiz: {error_data.get('error', 'Unknown error')}")
                return None
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    def submit_quiz(self, quiz_id, answers):
        """Submit quiz answers"""
        try:
            payload = {
                'answers': answers
            }
            response = requests.post(f"{self.api_base_url}/{quiz_id}/submit/", json=payload)
            
            if response.status_code == 201:
                return response.json()
            else:
                error_data = response.json()
                st.error(f"Failed to submit quiz: {error_data.get('error', 'Unknown error')}")
                return None
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    def regenerate_insights(self, result_id):
        """Regenerate insights for a quiz result"""
        try:
            response = requests.post(f"{self.api_base_url}/results/{result_id}/regenerate/")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                st.error(f"Failed to regenerate insights: {error_data.get('error', 'Unknown error')}")
                return None
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    def like_insight(self, result_id):
        """Mark insight as liked"""
        try:
            response = requests.post(f"{self.api_base_url}/results/{result_id}/like/")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def dislike_insight(self, result_id):
        """Mark insight as disliked"""
        try:
            response = requests.post(f"{self.api_base_url}/results/{result_id}/dislike/")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def reset_quiz(self):
        """Reset quiz session state"""
        st.session_state.quiz_data = None
        st.session_state.quiz_answers = {}
        st.session_state.quiz_result = None
        st.session_state.show_results = False
    
    def render_quiz_interface(self):
        """Render the main quiz interface"""
        self.initialize_session_state()
        
        # Custom CSS for styling
        st.markdown("""
        <style>
        .quiz-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .quiz-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .quiz-subtitle {
            color: #f0f0f0;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .question-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .insight-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1.5rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="quiz-container">
            <h1 class="quiz-title">✨ MindBuddy Wellness Quiz ✨</h1>
            <p class="quiz-subtitle">Track your well-being over time. Get personalized, adaptive insights to support your journey.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main interface logic
        if not st.session_state.show_results:
            self._render_quiz_setup()
        else:
            self._render_results()
    
    def _render_quiz_setup(self):
        """Render quiz setup and questions"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Get topics
            topics = self.get_topics()
            default_topics = [
                "Managing Daily Stress", "Improving Sleep Quality", "Building Mindfulness Habits", 
                "Work-Life Balance", "Practicing Self-Compassion", "Overcoming Procrastination",
                "Fostering Positive Thinking", "Understanding My Emotions", "Building Healthy Relationships"
            ]
            
            all_topics = topics if topics else default_topics
            
            selected_topic = st.selectbox(
                "Choose a topic or type your own:",
                options=all_topics + ["Custom"],
                key="topic_select"
            )
            
            if selected_topic == "Custom":
                selected_topic = st.text_input("Enter your custom topic:")
        
        with col2:
            quiz_length = st.radio(
                "Select Quiz Length:",
                options=["3 Questions", "5 Questions", "8 Questions"],
                key="length_select"
            )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Start Quiz", type="primary", use_container_width=True):
                if selected_topic and quiz_length:
                    length = int(quiz_length.split(" ")[0])
                    quiz_data = self.create_quiz(selected_topic, length)
                    
                    if quiz_data:
                        st.session_state.quiz_data = quiz_data
                        st.session_state.quiz_answers = {}
                        st.rerun()
                else:
                    st.warning("Please select both a topic and quiz length!")
        
        # Display quiz questions if quiz is created
        if st.session_state.quiz_data:
            self._render_quiz_questions()
    
    def _render_quiz_questions(self):
        """Render quiz questions"""
        quiz_data = st.session_state.quiz_data
        questions = quiz_data['questions_data']
        
        st.markdown("---")
        st.markdown("### Quiz Questions")
        
        # Display questions
        for i, question_data in enumerate(questions):
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <h4>Question {i+1}: {question_data['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                answer = st.radio(
                    "Select your answer:",
                    options=question_data['options'],
                    key=f"question_{i}",
                    label_visibility="collapsed"
                )
                
                st.session_state.quiz_answers[i] = answer
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Reset Quiz", type="secondary", use_container_width=True):
                self.reset_quiz()
                st.rerun()
        
        with col3:
            if st.button("Get My Insights & See Progress", type="primary", use_container_width=True):
                # Check if all questions are answered
                if len(st.session_state.quiz_answers) == len(questions):
                    # Convert answers to list
                    answers_list = [st.session_state.quiz_answers[i] for i in range(len(questions))]
                    
                    # Submit quiz
                    result = self.submit_quiz(quiz_data['id'], answers_list)
                    
                    if result:
                        st.session_state.quiz_result = result
                        st.session_state.show_results = True
                        st.rerun()
                else:
                    st.warning(f"Please answer all {len(questions)} questions before getting your insights.")
    
    def _render_results(self):
        """Render quiz results and insights"""
        if not st.session_state.quiz_result:
            return
        
        result = st.session_state.quiz_result
        
        # Display insights
        st.markdown(f"""
        <div class="insight-card">
            {result['insights']}
        </div>
        """, unsafe_allow_html=True)
        
        # Feedback buttons
        st.markdown("---")
        st.markdown("<p style='text-align: center; font-style: italic;'>Did you find this insight helpful?</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("👍 Like", type="secondary", use_container_width=True):
                if self.like_insight(result['id']):
                    st.success("Thank you for your feedback! I'm glad you found this helpful.")
                    st.session_state.show_feedback = False
        
        with col3:
            if st.button("👎 This wasn't for me", type="secondary", use_container_width=True):
                with st.spinner("Generating a new insight for you..."):
                    new_result = self.regenerate_insights(result['id'])
                    
                    if new_result:
                        st.session_state.quiz_result = new_result
                        st.info("I'm sorry that wasn't helpful. Here's a new insight for you:")
                        st.rerun()
        
        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Take Another Quiz", type="primary", use_container_width=True):
                self.reset_quiz()
                st.rerun()
    
    def render_quiz_history(self):
        """Render quiz history"""
        try:
            response = requests.get(f"{self.api_base_url}/history/")
            if response.status_code == 200:
                history = response.json()
                
                if history:
                    st.markdown("### Your Quiz History")
                    
                    for entry in history:
                        with st.expander(f"{entry['topic_name']} - {entry['date'][:10]}"):
                            st.write("**Your answers:**")
                            for item in entry['results_data']:
                                st.write(f"- {item['question']}: **{item['answer']}**")
                else:
                    st.info("No quiz history found. Take your first quiz to get started!")
            else:
                st.error("Failed to load quiz history")
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")

# Usage example function
def main():
    """Main function to demonstrate the quiz component"""
    st.set_page_config(
        page_title="MindBuddy Wellness Quiz",
        page_icon="✨",
        layout="wide"
    )
    
    quiz_component = QuizComponent()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Take Quiz", "Quiz History"])
    
    if page == "Take Quiz":
        quiz_component.render_quiz_interface()
    elif page == "Quiz History":
        quiz_component.render_quiz_history()

if __name__ == "__main__":
    main()