"""
MindBuddy Analytics Module
Handles analytics and data visualization for mood tracking
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
from api_client import MindBuddyAPI, get_mood_emoji

def analytics_interface(user_token):
    """Main analytics interface"""
    st.markdown("### 📊 Your Wellness Analytics")
    
    # Time period selector
    period = _display_time_selector()
    
    # Get mood history
    with st.spinner("Loading your wellness data... 📊"):
        if st.session_state.is_demo:
            mood_history = _get_demo_analytics_data(period)
            time.sleep(1)  # Simulate loading
        else:
            mood_history = MindBuddyAPI.get_mood_history(period, token=user_token)
    
    if mood_history and mood_history.get('chart_data'):
        # Statistics overview
        _display_statistics_overview(mood_history, period)
        
        # Main mood chart
        _display_mood_trend_chart(mood_history)
        
        # Multi-metric chart
        _display_multi_metric_chart(mood_history)
        
        # Enhanced insights section
        _display_insights_section(mood_history, period)
    else:
        _display_no_data_message()

def _display_time_selector():
    """Display time period selector"""
    col1, col2 = st.columns([3, 1])
    with col1:
        period = st.selectbox(
            "📅 Select Time Period",
            options=[7, 14, 30, 60, 90],
            format_func=lambda x: f"Last {x} days",
            index=2  # Default to 30 days
        )
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    return period

def _get_demo_analytics_data(period):
    """Generate extended demo data for analytics"""
    return {
        "chart_data": [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
             "mood_rating": 2 + (i % 4), "energy_level": 1 + (i % 5), 
             "anxiety_level": 5 - (i % 4), "has_entry": True}
            for i in range(period, 0, -1)
        ],
        "statistics": {
            "average_mood": 3.2, "tracking_percentage": 87, 
            "total_entries": period - 3, "best_mood": 5
        }
    }

def _display_statistics_overview(mood_history, period):
    """Display statistics overview cards"""
    stats = mood_history.get('statistics', {})
    if stats:
        st.markdown("#### 📈 Period Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_mood = stats.get('average_mood', 0)
            st.metric(
                "Average Mood", 
                f"{avg_mood:.1f}/5",
                delta=f"{get_mood_emoji(round(avg_mood))}"
            )
        
        with col2:
            tracking_pct = stats.get('tracking_percentage', 0)
            delta_text = "Great!" if tracking_pct >= 80 else "Keep going!"
            st.metric("Tracking Consistency", f"{tracking_pct:.0f}%", delta=delta_text)
        
        with col3:
            best_mood = stats.get('best_mood', 0)
            st.metric("Best Mood", f"{best_mood}/5", delta=get_mood_emoji(best_mood))
        
        with col4:
            total_entries = stats.get('total_entries', 0)
            st.metric("Total Entries", total_entries, delta=f"out of {period} days")

def _display_mood_trend_chart(mood_history):
    """Display the main mood trend chart"""
    st.markdown("#### 🌈 Mood Trend Analysis")
    fig = create_mood_chart(mood_history)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="mood_trend_chart")

def _display_multi_metric_chart(mood_history):
    """Display the multi-metric comprehensive chart"""
    st.markdown("#### 📊 Comprehensive Wellness Tracking")
    multi_fig = create_multi_metric_chart(mood_history)
    if multi_fig:
        st.plotly_chart(multi_fig, use_container_width=True, key="multi_metric_chart")

def _display_insights_section(mood_history, period):
    """Display wellness insights"""
    st.markdown("#### 💡 Wellness Insights")
    
    chart_data = mood_history['chart_data']
    entries_with_data = [entry for entry in chart_data if entry['has_entry']]
    
    if entries_with_data:
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            _display_trend_analysis(entries_with_data)
            _display_consistency_insight(mood_history.get('statistics', {}))
        
        with insight_col2:
            _display_mood_distribution_insight(entries_with_data)
            _display_energy_mood_correlation(entries_with_data)

def _display_trend_analysis(entries_with_data):
    """Display trend analysis insight"""
    recent_moods = [entry['mood_rating'] for entry in entries_with_data[-7:]]
    if len(recent_moods) >= 3:
        if recent_moods[-1] > recent_moods[0]:
            trend, trend_emoji = "improving", "📈"
        elif recent_moods[-1] < recent_moods[0]:
            trend, trend_emoji = "declining", "📉"
        else:
            trend, trend_emoji = "stable", "➡️"
        
        st.info(f"{trend_emoji} Your mood trend over the last week appears to be **{trend}**.")

def _display_consistency_insight(stats):
    """Display consistency insight"""
    consistency = stats.get('tracking_percentage', 0)
    if consistency >= 80:
        st.success("🌟 Excellent tracking consistency! You're building a great habit.")
    elif consistency >= 60:
        st.info("👍 Good tracking consistency! Keep up the momentum.")
    else:
        st.warning("💪 Try to log your mood more regularly for better insights.")

def _display_mood_distribution_insight(entries_with_data):
    """Display mood distribution insight"""
    mood_counts = {}
    for entry in entries_with_data:
        mood = entry['mood_rating']
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    if mood_counts:
        most_common_mood = max(mood_counts, key=mood_counts.get)
        st.info(f"{get_mood_emoji(most_common_mood)} Your most common mood rating is **{most_common_mood}/5**.")

def _display_energy_mood_correlation(entries_with_data):
    """Display energy vs mood correlation insight"""
    moods = [entry['mood_rating'] for entry in entries_with_data]
    energies = [entry['energy_level'] for entry in entries_with_data]
    if len(moods) > 3:
        avg_mood = sum(moods) / len(moods)
        avg_energy = sum(energies) / len(energies)
        
        if abs(avg_mood - avg_energy) < 0.5:
            st.success("⚡ Your mood and energy levels are well-balanced!")
        elif avg_energy < avg_mood:
            st.info("🔋 Consider activities that boost your energy levels.")
        else:
            st.info("😌 Your energy is great! Focus on mood-boosting activities.")

def _display_no_data_message():
    """Display message when no data is available"""
    st.markdown("""
    <div class="custom-card" style="text-align: center;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
        <h3 style="color: #ffffff;">Start Your Wellness Journey!</h3>
        <p style="color: #b8b8b8; font-size: 1.1rem;">
            Begin logging your mood to see beautiful analytics and insights here.
        </p>
        <p style="color: #b8b8b8;">
            Use the <strong>Log Mood</strong> tab to get started! ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_mood_chart(data):
    """Create beautiful mood trend chart with dark theme"""
    if not data or not data.get('chart_data'):
        return None
    
    df = pd.DataFrame(data['chart_data'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter entries with data
    df_with_data = df[df['has_entry'] == True].copy()
    
    if df_with_data.empty:
        return None
    
    # Create the mood trend chart
    fig = go.Figure()
    
    # Add mood line with gradient
    fig.add_trace(go.Scatter(
        x=df_with_data['date'],
        y=df_with_data['mood_rating'],
        mode='lines+markers',
        name='Mood Rating',
        line=dict(color='#667eea', width=4, shape='spline'),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Mood: %{y}/5<extra></extra>',
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # Customize layout for dark theme
    fig.update_layout(
        title={
            'text': '🌈 Your Mood Journey',
            'x': 0.5,
            'font': {'size': 28, 'family': 'Poppins', 'color': 'white'}
        },
        xaxis_title="Date",
        yaxis_title="Mood Rating",
        yaxis=dict(range=[0.5, 5.5], tickmode='linear', dtick=1),
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color='white'),
        hovermode='x unified'
    )
    
    # Dark theme grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_multi_metric_chart(data):
    """Create multi-metric comparison chart with dark theme"""
    if not data or not data.get('chart_data'):
        return None
    
    df = pd.DataFrame(data['chart_data'])
    df['date'] = pd.to_datetime(df['date'])
    df_with_data = df[df['has_entry'] == True].copy()
    
    if df_with_data.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('🌟 Mood Rating', '⚡ Energy Level', '😰 Anxiety Level'),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # Add traces with enhanced styling
    colors = ['#667eea', '#38ef7d', '#FFA726']
    metrics = ['mood_rating', 'energy_level', 'anxiety_level']
    
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        fig.add_trace(
            go.Scatter(
                x=df_with_data['date'], y=df_with_data[metric],
                mode='lines+markers', 
                line=dict(color=color, width=3),
                marker=dict(size=8, line=dict(width=2, color='white')),
                fill='tonexty',
                fillcolor=f'rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.1])}'
            ), row=i+1, col=1
        )
    
    # Update layout for dark theme
    fig.update_layout(
        title={
            'text': '📊 Comprehensive Wellness Tracking',
            'x': 0.5,
            'font': {'size': 24, 'family': 'Poppins', 'color': 'white'}
        },
        height=650,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color='white')
    )
    
    # Update axes
    for i in range(1, 4):
        fig.update_yaxes(range=[0.5, 5.5], row=i, col=1)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)', row=i, col=1)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)', row=i, col=1)
    
    return fig