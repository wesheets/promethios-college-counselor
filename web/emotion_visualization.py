"""
Emotion visualization dashboard for the Promethios College Counselor.

This module provides visualization of student emotional states over time based on journal entries.
"""

import datetime
from flask import jsonify, render_template, request, session
import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class EmotionVisualization:
    """Generates visualizations of student emotional states over time."""
    
    def __init__(self, journal_entries=None):
        """
        Initialize the emotion visualization module.
        
        Args:
            journal_entries: Optional list of journal entries to analyze
        """
        self.journal_entries = journal_entries or []
    
    def set_journal_entries(self, journal_entries):
        """
        Set the journal entries to analyze.
        
        Args:
            journal_entries: List of journal entries
        """
        self.journal_entries = journal_entries
    
    def generate_emotion_timeline(self, days=30):
        """
        Generate timeline visualization of emotional states.
        
        Args:
            days: Number of days to include
            
        Returns:
            dict: Timeline visualization data
        """
        # Filter by date range
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        filtered_entries = [
            entry for entry in self.journal_entries 
            if entry.created_at >= start_date
        ]
        
        # Sort entries by date
        filtered_entries.sort(key=lambda x: x.created_at)
        
        # Extract emotional data points
        data_points = []
        for entry in filtered_entries:
            sentiment = entry.sentiment_score
            uncertainty = entry.uncertainty_score
            agitation = entry.agitation_score
            
            data_points.append({
                "date": entry.created_at.strftime("%Y-%m-%d"),
                "timestamp": entry.created_at.isoformat(),
                "title": entry.title or "Untitled Entry",
                "id": entry.id,
                "sentiment": sentiment,
                "uncertainty": uncertainty,
                "agitation": agitation,
                "color": self._get_emotion_color(sentiment, uncertainty, agitation)
            })
        
        # Calculate averages
        if data_points:
            avg_sentiment = sum(p["sentiment"] for p in data_points) / len(data_points)
            avg_uncertainty = sum(p["uncertainty"] for p in data_points) / len(data_points)
            avg_agitation = sum(p["agitation"] for p in data_points) / len(data_points)
        else:
            avg_sentiment = 50
            avg_uncertainty = 50
            avg_agitation = 50
        
        return {
            "timeline": data_points,
            "average_sentiment": avg_sentiment,
            "average_uncertainty": avg_uncertainty,
            "average_agitation": avg_agitation
        }
    
    def _get_emotion_color(self, sentiment, uncertainty, agitation):
        """
        Generate color based on emotional state.
        
        Args:
            sentiment: Sentiment score (0-100)
            uncertainty: Uncertainty score (0-100)
            agitation: Agitation score (0-100)
            
        Returns:
            str: RGB color string
        """
        # Red component based on sentiment (lower sentiment = more red)
        r = int(255 * (1 - sentiment/100))
        
        # Green component based on uncertainty (lower uncertainty = more green)
        g = int(255 * (1 - uncertainty/100))
        
        # Blue component based on agitation (lower agitation = more blue)
        b = int(255 * (1 - agitation/100))
        
        return f"rgb({r},{g},{b})"
    
    def generate_emotion_radar_chart(self):
        """
        Generate radar chart of average emotional states.
        
        Returns:
            str: JSON string of plotly figure
        """
        # Get emotion timeline data
        data = self.generate_emotion_timeline()
        
        # Create radar chart
        categories = ['Sentiment', 'Certainty', 'Calmness']
        values = [
            data["average_sentiment"],
            100 - data["average_uncertainty"],  # Convert uncertainty to certainty
            100 - data["average_agitation"]     # Convert agitation to calmness
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Emotional State',
            line_color='rgba(54, 162, 235, 1)',
            fillcolor='rgba(54, 162, 235, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_emotion_line_chart(self):
        """
        Generate line chart of emotional states over time.
        
        Returns:
            str: JSON string of plotly figure
        """
        # Get emotion timeline data
        data = self.generate_emotion_timeline()
        timeline = data["timeline"]
        
        if not timeline:
            # Create empty chart if no data
            fig = go.Figure()
            fig.update_layout(
                title="No journal entries found",
                xaxis_title="Date",
                yaxis_title="Score",
                yaxis=dict(range=[0, 100])
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Create dataframe
        df = pd.DataFrame(timeline)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sentiment'],
            mode='lines+markers',
            name='Sentiment',
            line=dict(color='rgba(54, 162, 235, 1)', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['uncertainty'],
            mode='lines+markers',
            name='Uncertainty',
            line=dict(color='rgba(255, 99, 132, 1)', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['agitation'],
            mode='lines+markers',
            name='Agitation',
            line=dict(color='rgba(255, 206, 86, 1)', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Emotional State Over Time",
            xaxis_title="Date",
            yaxis_title="Score",
            yaxis=dict(range=[0, 100]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_emotion_heatmap(self):
        """
        Generate heatmap of emotional states over time.
        
        Returns:
            str: JSON string of plotly figure
        """
        # Get emotion timeline data
        data = self.generate_emotion_timeline()
        timeline = data["timeline"]
        
        if not timeline:
            # Create empty chart if no data
            fig = go.Figure()
            fig.update_layout(
                title="No journal entries found",
                xaxis_title="Date",
                yaxis_title="Emotion"
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Create dataframe
        df = pd.DataFrame(timeline)
        df['date'] = pd.to_datetime(df['date'])
        
        # Reshape data for heatmap
        emotions = ['Sentiment', 'Uncertainty', 'Agitation']
        heatmap_data = []
        
        for entry in timeline:
            heatmap_data.append({
                'Date': entry['date'],
                'Emotion': 'Sentiment',
                'Score': entry['sentiment']
            })
            heatmap_data.append({
                'Date': entry['date'],
                'Emotion': 'Uncertainty',
                'Score': entry['uncertainty']
            })
            heatmap_data.append({
                'Date': entry['date'],
                'Emotion': 'Agitation',
                'Score': entry['agitation']
            })
        
        heatmap_df = pd.DataFrame(heatmap_data)
        heatmap_df['Date'] = pd.to_datetime(heatmap_df['Date'])
        
        # Create heatmap
        fig = px.density_heatmap(
            heatmap_df,
            x='Date',
            y='Emotion',
            z='Score',
            color_continuous_scale='Viridis',
            range_color=[0, 100]
        )
        
        fig.update_layout(
            title="Emotional State Heatmap",
            xaxis_title="Date",
            yaxis_title="Emotion"
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_emotion_summary(self):
        """
        Generate summary of emotional states.
        
        Returns:
            dict: Summary data
        """
        # Get emotion timeline data
        data = self.generate_emotion_timeline()
        timeline = data["timeline"]
        
        # Calculate trends
        sentiment_trend = self._calculate_trend([p["sentiment"] for p in timeline]) if timeline else 0
        uncertainty_trend = self._calculate_trend([p["uncertainty"] for p in timeline]) if timeline else 0
        agitation_trend = self._calculate_trend([p["agitation"] for p in timeline]) if timeline else 0
        
        # Generate summary text
        summary = self._generate_summary_text(
            data["average_sentiment"],
            data["average_uncertainty"],
            data["average_agitation"],
            sentiment_trend,
            uncertainty_trend,
            agitation_trend
        )
        
        return {
            "average_sentiment": data["average_sentiment"],
            "average_uncertainty": data["average_uncertainty"],
            "average_agitation": data["average_agitation"],
            "sentiment_trend": sentiment_trend,
            "uncertainty_trend": uncertainty_trend,
            "agitation_trend": agitation_trend,
            "summary": summary
        }
    
    def _calculate_trend(self, values):
        """
        Calculate trend from a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            float: Trend value (-1 to 1)
        """
        if not values or len(values) < 2:
            return 0
        
        # Use linear regression to calculate trend
        x = np.array(range(len(values)))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize to -1 to 1 range
        max_slope = 10  # Maximum expected slope
        normalized_slope = max(-1, min(1, slope / max_slope))
        
        return normalized_slope
    
    def _generate_summary_text(self, sentiment, uncertainty, agitation, 
                              sentiment_trend, uncertainty_trend, agitation_trend):
        """
        Generate summary text based on emotional states and trends.
        
        Returns:
            str: Summary text
        """
        # Determine overall emotional state
        if sentiment >= 70 and uncertainty <= 30 and agitation <= 30:
            state = "positive and confident"
        elif sentiment >= 50 and uncertainty <= 50 and agitation <= 50:
            state = "generally positive"
        elif sentiment <= 30 and uncertainty >= 70:
            state = "negative and uncertain"
        elif sentiment <= 30 and agitation >= 70:
            state = "negative and agitated"
        elif uncertainty >= 70:
            state = "very uncertain"
        elif agitation >= 70:
            state = "very agitated"
        else:
            state = "mixed"
        
        # Determine trend direction
        if sentiment_trend > 0.3 and uncertainty_trend < -0.3:
            trend = "improving"
        elif sentiment_trend < -0.3 and (uncertainty_trend > 0.3 or agitation_trend > 0.3):
            trend = "declining"
        elif abs(sentiment_trend) < 0.2 and abs(uncertainty_trend) < 0.2 and abs(agitation_trend) < 0.2:
            trend = "stable"
        else:
            trend = "fluctuating"
        
        # Generate summary
        summary = f"Your emotional state appears to be {state} and {trend}. "
        
        # Add specific insights
        if sentiment < 40:
            summary += "Your sentiment is relatively low, which might affect how you perceive college options. "
        
        if uncertainty > 60:
            summary += "Your high uncertainty suggests you might benefit from more information or guidance. "
        
        if agitation > 60:
            summary += "Your elevated agitation indicates this process may be causing stress. "
        
        # Add recommendations
        if state == "positive and confident":
            summary += "This is an ideal emotional state for making college decisions."
        elif state == "generally positive":
            summary += "This is a good emotional state for exploring options."
        elif state == "negative and uncertain":
            summary += "Consider talking to a counselor or trusted mentor to help clarify your thoughts."
        elif state == "negative and agitated":
            summary += "It might be helpful to take a break from the college search process for a few days."
        elif state == "very uncertain":
            summary += "Breaking down the decision process into smaller steps might help reduce uncertainty."
        elif state == "very agitated":
            summary += "Practicing relaxation techniques before making decisions could be beneficial."
        else:
            summary += "Continue journaling to help clarify your thoughts and feelings."
        
        return summary

# Flask routes for emotion visualization
def register_emotion_visualization_routes(app, db):
    """
    Register Flask routes for emotion visualization.
    
    Args:
        app: Flask application
        db: SQLAlchemy database
    """
    from models import JournalEntry, User
    
    @app.route('/emotion-dashboard', methods=['GET'])
    def emotion_dashboard():
        """Render emotion visualization dashboard."""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Get journal entries
        entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
        
        # Initialize visualization
        visualizer = EmotionVisualization(entries)
        
        # Generate charts
        radar_chart = visualizer.generate_emotion_radar_chart()
        line_chart = visualizer.generate_emotion_line_chart()
        heatmap = visualizer.generate_emotion_heatmap()
        
        # Generate summary
        summary = visualizer.generate_emotion_summary()
        
        return render_template(
            'emotion_dashboard.html',
            user=user,
            radar_chart=radar_chart,
            line_chart=line_chart,
            heatmap=heatmap,
            summary=summary
        )
    
    @app.route('/api/emotion-data', methods=['GET'])
    def emotion_data():
        """API endpoint for emotion data."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Get journal entries
        entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
        
        # Initialize visualization
        visualizer = EmotionVisualization(entries)
        
        # Get days parameter
        days = request.args.get('days', default=30, type=int)
        
        # Generate timeline data
        timeline_data = visualizer.generate_emotion_timeline(days=days)
        
        return jsonify(timeline_data)
