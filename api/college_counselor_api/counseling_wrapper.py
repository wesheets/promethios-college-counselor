"""
Counseling Wrapper - Core Logic for College Counselor

This module implements the core counseling logic, including trust evaluation,
emotional state analysis, and recommendation generation.
"""

import json
import datetime
import sys
import os

# Add the parent directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from promethios_core.governance_core import GovernanceCore

class BaseTrustFactor:
    """Base class for all trust factors."""
    
    def __init__(self, name, weight=1.0):
        self.name = name
        self.weight = weight
        self.score = None
        self.explanation = None
        
    def evaluate(self, data):
        """
        Evaluate the trust factor based on input data.
        
        Args:
            data: Dictionary containing relevant data for evaluation
            
        Returns:
            float: Score between 0 and 100
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
    
    def get_score(self):
        """Get the calculated score."""
        if self.score is None:
            raise ValueError("Factor has not been evaluated yet")
        return self.score
    
    def get_explanation(self):
        """Get explanation for the score."""
        if self.explanation is None:
            raise ValueError("Factor has not been evaluated yet")
        return self.explanation


class GPAEvaluator:
    """Evaluates GPA match between student and college."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate GPA match.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_gpa = student_profile.get('gpa', 0)
        college_avg_gpa = college.get('average_gpa', 0)
        
        if college_avg_gpa == 0:
            # No GPA data available for college
            return 50
        
        # Calculate difference
        diff = student_gpa - college_avg_gpa
        
        # Score based on difference
        if diff >= 0.5:
            # Student GPA is significantly higher
            return 90
        elif diff >= 0.3:
            # Student GPA is moderately higher
            return 80
        elif diff >= 0:
            # Student GPA is slightly higher
            return 70
        elif diff >= -0.3:
            # Student GPA is slightly lower
            return 60
        elif diff >= -0.5:
            # Student GPA is moderately lower
            return 40
        else:
            # Student GPA is significantly lower
            return 20


class MajorMatchEvaluator:
    """Evaluates major match between student and college."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate major match.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_majors = student_profile.get('intended_majors', [])
        college_majors = college.get('majors', [])
        
        if not student_majors or not college_majors:
            # No major data available
            return 50
        
        # Count matches
        matches = sum(1 for major in student_majors if major in college_majors)
        
        # Calculate score based on matches
        if matches == len(student_majors):
            # All majors match
            return 100
        elif matches > 0:
            # Some majors match
            return 70
        else:
            # No majors match
            return 30


class LocationPreferenceEvaluator:
    """Evaluates location preference match between student and college."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate location preference match.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_location = student_profile.get('location_preference', '')
        college_location = college.get('location', {})
        college_state = college_location.get('state', '')
        
        if not student_location or not college_state:
            # No location data available
            return 50
        
        # Check for exact match
        if student_location.lower() == college_state.lower():
            return 100
        
        # Check for regional match (simplified)
        northeast = ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA']
        midwest = ['OH', 'MI', 'IN', 'IL', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS']
        south = ['DE', 'MD', 'DC', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL', 'KY', 'TN', 'AL', 'MS', 'AR', 'LA', 'OK', 'TX']
        west = ['MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV', 'WA', 'OR', 'CA', 'AK', 'HI']
        
        regions = {
            'northeast': northeast,
            'midwest': midwest,
            'south': south,
            'west': west
        }
        
        # Check if student preference is a region
        if student_location.lower() in regions:
            if college_state.upper() in regions[student_location.lower()]:
                return 80
        
        # Check if both are in the same region
        student_region = None
        college_region = None
        
        for region, states in regions.items():
            if student_location.upper() in states:
                student_region = region
            if college_state.upper() in states:
                college_region = region
        
        if student_region and college_region and student_region == college_region:
            return 70
        
        # No match
        return 30


class AcademicProfileFactor(BaseTrustFactor):
    """Evaluates the academic profile of the student."""
    
    def __init__(self, weight=1.0):
        super().__init__("Academic Profile", weight)
        self.gpa_evaluator = GPAEvaluator()
        self.major_match_evaluator = MajorMatchEvaluator()
        self.location_preference_evaluator = LocationPreferenceEvaluator()
        
    def evaluate(self, data):
        """
        Evaluate academic profile based on GPA, major match, and location preference.
        
        Args:
            data: Dictionary containing student profile and college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_profile = data.get("student_profile", {})
        college = data.get("college", {})
        
        gpa_score = self.gpa_evaluator.evaluate(student_profile, college)
        major_match_score = self.major_match_evaluator.evaluate(student_profile, college)
        location_score = self.location_preference_evaluator.evaluate(student_profile, college)
        
        # Calculate weighted average
        self.score = (gpa_score * 0.5 + 
                      major_match_score * 0.3 + 
                      location_score * 0.2)
        
        # Generate explanation
        self.explanation = {
            "factor": self.name,
            "score": self.score,
            "components": {
                "gpa_match": gpa_score,
                "major_match": major_match_score,
                "location_match": location_score
            },
            "summary": self._generate_summary(gpa_score, major_match_score, location_score)
        }
        
        return self.score
    
    def _generate_summary(self, gpa_score, major_match_score, location_score):
        """Generate a summary explanation based on component scores."""
        if gpa_score < 50:
            return "Your GPA is below the typical range for this college."
        elif major_match_score < 50:
            return "Your intended major may not be a strong match for this college."
        elif location_score < 50:
            return "This college doesn't align well with your location preferences."
        else:
            return "Your academic profile is a good match for this college."


class SentimentEvaluator:
    """Evaluates sentiment in text."""
    
    def evaluate(self, entry):
        """
        Evaluate sentiment in text.
        
        Args:
            entry: Dictionary containing journal entry data
            
        Returns:
            float: Score between 0 and 100
        """
        # For demo purposes, use a simple mock implementation
        # In production, this would use the OpenAI API
        
        text = entry.get('text', '').lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ['happy', 'excited', 'confident', 'hopeful', 'good', 'great', 'excellent']
        negative_words = ['sad', 'anxious', 'worried', 'stressed', 'bad', 'terrible', 'awful']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate score
        if positive_count == 0 and negative_count == 0:
            return 50
        
        total = positive_count + negative_count
        positive_ratio = positive_count / total if total > 0 else 0.5
        
        # Convert to score (0-100)
        return positive_ratio * 100


class UncertaintyEvaluator:
    """Evaluates uncertainty in text."""
    
    def evaluate(self, entry):
        """
        Evaluate uncertainty in text.
        
        Args:
            entry: Dictionary containing journal entry data
            
        Returns:
            float: Score between 0 and 100 (0 = highly uncertain, 100 = certain)
        """
        # For demo purposes, use a simple mock implementation
        # In production, this would use the OpenAI API
        
        text = entry.get('text', '').lower()
        
        # Simple keyword-based uncertainty analysis
        uncertainty_words = ['maybe', 'perhaps', 'not sure', 'uncertain', 'doubt', 'confused', 'unsure', 'might', 'could']
        certainty_words = ['definitely', 'certainly', 'sure', 'know', 'confident', 'absolutely', 'without doubt']
        
        uncertainty_count = sum(1 for word in uncertainty_words if word in text)
        certainty_count = sum(1 for word in certainty_words if word in text)
        
        # Calculate score
        if uncertainty_count == 0 and certainty_count == 0:
            return 50
        
        total = uncertainty_count + certainty_count
        certainty_ratio = certainty_count / total if total > 0 else 0.5
        
        # Convert to score (0-100)
        return certainty_ratio * 100


class AgitationEvaluator:
    """Evaluates agitation in text."""
    
    def evaluate(self, entry):
        """
        Evaluate agitation in text.
        
        Args:
            entry: Dictionary containing journal entry data
            
        Returns:
            float: Score between 0 and 100 (0 = highly agitated, 100 = calm)
        """
        # For demo purposes, use a simple mock implementation
        # In production, this would use the OpenAI API
        
        text = entry.get('text', '').lower()
        
        # Simple keyword-based agitation analysis
        agitation_words = ['angry', 'frustrated', 'upset', 'annoyed', 'mad', 'furious', 'stressed', 'overwhelmed']
        calm_words = ['calm', 'relaxed', 'peaceful', 'serene', 'tranquil', 'composed', 'collected']
        
        agitation_count = sum(1 for word in agitation_words if word in text)
        calm_count = sum(1 for word in calm_words if word in text)
        
        # Calculate score
        if agitation_count == 0 and calm_count == 0:
            return 50
        
        total = agitation_count + calm_count
        calm_ratio = calm_count / total if total > 0 else 0.5
        
        # Convert to score (0-100)
        return calm_ratio * 100


class EmotionalStateFactor(BaseTrustFactor):
    """Evaluates the emotional state of the student based on journaling."""
    
    def __init__(self, weight=1.2):  # Higher weight due to importance
        super().__init__("Emotional State", weight)
        self.sentiment_evaluator = SentimentEvaluator()
        self.uncertainty_evaluator = UncertaintyEvaluator()
        self.agitation_evaluator = AgitationEvaluator()
        
    def evaluate(self, data):
        """
        Evaluate emotional state based on journal entries.
        
        Args:
            data: Dictionary containing journal entries and other data
            
        Returns:
            float: Score between 0 and 100
        """
        journal_entries = data.get("journal_entries", [])
        
        if not journal_entries:
            # No journal entries to evaluate
            self.score = 100  # Default to neutral/positive
            self.explanation = {
                "factor": self.name,
                "score": self.score,
                "components": {
                    "sentiment": 100,
                    "uncertainty": 100,
                    "agitation": 100
                },
                "summary": "No journal entries to evaluate emotional state."
            }
            return self.score
        
        # Get the most recent journal entry
        latest_entry = journal_entries[-1]
        
        sentiment_score = self.sentiment_evaluator.evaluate(latest_entry)
        uncertainty_score = self.uncertainty_evaluator.evaluate(latest_entry)
        agitation_score = self.agitation_evaluator.evaluate(latest_entry)
        
        # Calculate weighted average
        # Lower scores indicate more negative emotions or higher uncertainty/agitation
        self.score = (sentiment_score * 0.4 + 
                      uncertainty_score * 0.3 + 
                      agitation_score * 0.3)
        
        # Generate explanation
        self.explanation = {
            "factor": self.name,
            "score": self.score,
            "components": {
                "sentiment": sentiment_score,
                "uncertainty": uncertainty_score,
                "agitation": agitation_score
            },
            "summary": self._generate_summary(sentiment_score, uncertainty_score, agitation_score)
        }
        
        return self.score
    
    def _generate_summary(self, sentiment_score, uncertainty_score, agitation_score):
        """Generate a summary explanation based on component scores."""
        if agitation_score < 30:
            return "Your journal entry indicates significant agitation. Consider taking a break before making decisions."
        elif uncertainty_score < 30:
            return "Your journal entry shows high uncertainty. It might help to discuss your concerns with a counselor."
        elif sentiment_score < 30:
            return "Your journal entry reflects negative emotions. Consider exploring these feelings further."
        else:
            return "Your emotional state appears balanced for decision-making."


class AdmissionLikelihoodEvaluator:
    """Evaluates likelihood of admission based on student profile and college data."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate admission likelihood.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_gpa = student_profile.get('gpa', 0)
        college_avg_gpa = college.get('average_gpa', 0)
        admission_rate = college.get('admission_rate', 0)
        
        if college_avg_gpa == 0:
            # No GPA data available for college
            return 50
        
        # Calculate GPA difference
        gpa_diff = student_gpa - college_avg_gpa
        
        # Base score on GPA difference
        if gpa_diff >= 0.5:
            base_score = 90
        elif gpa_diff >= 0.3:
            base_score = 80
        elif gpa_diff >= 0:
            base_score = 70
        elif gpa_diff >= -0.3:
            base_score = 50
        elif gpa_diff >= -0.5:
            base_score = 30
        else:
            base_score = 10
        
        # Adjust based on admission rate
        if admission_rate > 0:
            # Lower score for more selective schools
            admission_factor = admission_rate * 100  # Convert to 0-100 scale
            
            # Weighted average of base score and admission factor
            return (base_score * 0.7) + (admission_factor * 0.3)
        else:
            return base_score


class SchoolFitEvaluator:
    """Evaluates overall fit between student and college."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate school fit.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        # For demo purposes, use a simple implementation
        # In production, this would use more sophisticated algorithms
        
        # Check for size preference match
        size_preference = student_profile.get('size_preference', '')
        enrollment = college.get('enrollment', 0)
        
        size_score = 50  # Default
        
        if size_preference and enrollment > 0:
            if size_preference == 'small' and enrollment < 5000:
                size_score = 90
            elif size_preference == 'medium' and 5000 <= enrollment < 15000:
                size_score = 90
            elif size_preference == 'large' and enrollment >= 15000:
                size_score = 90
            elif size_preference == 'small' and enrollment >= 15000:
                size_score = 10
            elif size_preference == 'large' and enrollment < 5000:
                size_score = 10
        
        # Check for campus setting preference match
        setting_preference = student_profile.get('setting_preference', '')
        campus_setting = college.get('campus_setting', '')
        
        setting_score = 50  # Default
        
        if setting_preference and campus_setting:
            if setting_preference.lower() == campus_setting.lower():
                setting_score = 90
            else:
                setting_score = 30
        
        # Calculate overall fit score
        return (size_score * 0.5) + (setting_score * 0.5)


class CollegeMatchFactor(BaseTrustFactor):
    """Evaluates the match between student and college."""
    
    def __init__(self, weight=1.0):
        super().__init__("College Match", weight)
        self.admission_likelihood_evaluator = AdmissionLikelihoodEvaluator()
        self.school_fit_evaluator = SchoolFitEvaluator()
        
    def evaluate(self, data):
        """
        Evaluate college match based on admission likelihood and school fit.
        
        Args:
            data: Dictionary containing student profile and college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_profile = data.get("student_profile", {})
        college = data.get("college", {})
        
        admission_score = self.admission_likelihood_evaluator.evaluate(student_profile, college)
        fit_score = self.school_fit_evaluator.evaluate(student_profile, college)
        
        # Calculate weighted average
        self.score = (admission_score * 0.6 + 
                      fit_score * 0.4)
        
        # Generate explanation
        self.explanation = {
            "factor": self.name,
            "score": self.score,
            "components": {
                "admission_likelihood": admission_score,
                "school_fit": fit_score
            },
            "summary": self._generate_summary(admission_score, fit_score)
        }
        
        return self.score
    
    def _generate_summary(self, admission_score, fit_score):
        """Generate a summary explanation based on component scores."""
        if admission_score < 30:
            return "This college may be a reach for your academic profile."
        elif fit_score < 30:
            return "This college may not be a good fit for your preferences."
        elif admission_score >= 70 and fit_score >= 70:
            return "This college is a strong match for both your academic profile and preferences."
        else:
            return "This college is a moderate match for your profile and preferences."


class CostEvaluator:
    """Evaluates cost of college against student budget."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate cost match.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_budget = student_profile.get('budget', 0)
        college_cost = college.get('cost', {}).get('total', 0)
        
        if student_budget == 0 or college_cost == 0:
            # No budget or cost data available
            return 50
        
        # Calculate ratio of budget to cost
        ratio = student_budget / college_cost if college_cost > 0 else 1
        
        # Convert ratio to score
        if ratio >= 1.2:
            # Budget is significantly higher than cost
            return 100
        elif ratio >= 1:
            # Budget is higher than or equal to cost
            return 90
        elif ratio >= 0.8:
            # Budget is slightly lower than cost
            return 70
        elif ratio >= 0.6:
            # Budget is moderately lower than cost
            return 50
        elif ratio >= 0.4:
            # Budget is significantly lower than cost
            return 30
        else:
            # Budget is much lower than cost
            return 10


class AffordabilityEvaluator:
    """Evaluates overall affordability of college."""
    
    def evaluate(self, student_profile, college):
        """
        Evaluate affordability.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            
        Returns:
            float: Score between 0 and 100
        """
        # For demo purposes, use a simple implementation
        # In production, this would consider financial aid, scholarships, etc.
        
        student_budget = student_profile.get('budget', 0)
        college_cost = college.get('cost', {}).get('total', 0)
        financial_aid = college.get('financial_aid', {}).get('average_package', 0)
        
        if student_budget == 0 or college_cost == 0:
            # No budget or cost data available
            return 50
        
        # Adjust cost based on financial aid
        adjusted_cost = college_cost - financial_aid if financial_aid > 0 else college_cost
        
        # Calculate ratio of budget to adjusted cost
        ratio = student_budget / adjusted_cost if adjusted_cost > 0 else 1
        
        # Convert ratio to score
        if ratio >= 1.2:
            # Budget is significantly higher than adjusted cost
            return 100
        elif ratio >= 1:
            # Budget is higher than or equal to adjusted cost
            return 90
        elif ratio >= 0.8:
            # Budget is slightly lower than adjusted cost
            return 70
        elif ratio >= 0.6:
            # Budget is moderately lower than adjusted cost
            return 50
        elif ratio >= 0.4:
            # Budget is significantly lower than adjusted cost
            return 30
        else:
            # Budget is much lower than adjusted cost
            return 10


class BudgetAlignmentFactor(BaseTrustFactor):
    """Evaluates the alignment between student budget and college cost."""
    
    def __init__(self, weight=0.8):
        super().__init__("Budget Alignment", weight)
        self.cost_evaluator = CostEvaluator()
        self.affordability_evaluator = AffordabilityEvaluator()
        
    def evaluate(self, data):
        """
        Evaluate budget alignment based on cost and affordability.
        
        Args:
            data: Dictionary containing student profile and college data
            
        Returns:
            float: Score between 0 and 100
        """
        student_profile = data.get("student_profile", {})
        college = data.get("college", {})
        
        cost_score = self.cost_evaluator.evaluate(student_profile, college)
        affordability_score = self.affordability_evaluator.evaluate(student_profile, college)
        
        # Calculate weighted average
        self.score = (cost_score * 0.7 + 
                      affordability_score * 0.3)
        
        # Generate explanation
        self.explanation = {
            "factor": self.name,
            "score": self.score,
            "components": {
                "cost_match": cost_score,
                "affordability": affordability_score
            },
            "summary": self._generate_summary(cost_score, affordability_score)
        }
        
        return self.score
    
    def _generate_summary(self, cost_score, affordability_score):
        """Generate a summary explanation based on component scores."""
        if cost_score < 30:
            return "This college's cost is significantly higher than your budget."
        elif affordability_score < 30:
            return "This college may not be affordable even with financial aid."
        elif cost_score >= 70 and affordability_score >= 70:
            return "This college aligns well with your budget and is affordable."
        else:
            return "This college is moderately aligned with your budget."


class TrustEvaluationFramework:
    """Framework for evaluating trust in college recommendations."""
    
    def __init__(self):
        self.factors = {
            "academic_profile": AcademicProfileFactor(weight=1.0),
            "emotional_state": EmotionalStateFactor(weight=1.2),
            "college_match": CollegeMatchFactor(weight=1.0),
            "budget_alignment": BudgetAlignmentFactor(weight=0.8)
        }
        self.results = None
        
    def evaluate(self, student_profile, college, journal_entries=None):
        """
        Evaluate all trust factors for a college recommendation.
        
        Args:
            student_profile: Dictionary containing student data
            college: Dictionary containing college data
            journal_entries: List of journal entries (optional)
            
        Returns:
            dict: Evaluation results with scores and explanations
        """
        # Prepare data for evaluation
        data = {
            "student_profile": student_profile,
            "college": college,
            "journal_entries": journal_entries or []
        }
        
        # Evaluate each factor
        factor_results = {}
        weighted_sum = 0
        total_weight = 0
        
        for factor_id, factor in self.factors.items():
            score = factor.evaluate(data)
            factor_results[factor_id] = {
                "score": score,
                "weight": factor.weight,
                "explanation": factor.get_explanation()
            }
            weighted_sum += score * factor.weight
            total_weight += factor.weight
        
        # Calculate overall trust score
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine recommendation category
        category = self._determine_category(overall_score, student_profile, college)
        
        # Store results
        self.results = {
            "overall_score": overall_score,
            "category": category,
            "factors": factor_results,
            "halt_recommended": self._check_for_halt(factor_results)
        }
        
        return self.results
    
    def _determine_category(self, overall_score, student_profile, college):
        """Determine if college is a reach, target, or safety school."""
        student_gpa = student_profile.get("gpa", 0)
        college_avg_gpa = college.get("average_gpa", 0)
        
        if student_gpa < college_avg_gpa - 0.3:
            return "reach"
        elif student_gpa > college_avg_gpa + 0.3:
            return "safety"
        else:
            return "target"
    
    def _check_for_halt(self, factor_results):
        """Check if emotional state indicates a halt is recommended."""
        emotional_state = factor_results.get("emotional_state", {})
        emotional_score = emotional_state.get("score", 100)
        
        # If emotional score is below threshold, recommend halt
        return emotional_score < 30


class JournalManager:
    """Manager for student journal entries."""
    
    def __init__(self):
        self.entries = {}
    
    def add_entry(self, student_id, entry_text):
        """
        Add a journal entry for a student.
        
        Args:
            student_id: ID of the student
            entry_text: Text of the journal entry
            
        Returns:
            dict: The created journal entry
        """
        if student_id not in self.entries:
            self.entries[student_id] = []
        
        entry = {
            "id": len(self.entries[student_id]) + 1,
            "text": entry_text,
            "timestamp": self._get_current_timestamp(),
            "emotional_state": None  # Will be populated by EmotionDetector
        }
        
        self.entries[student_id].append(entry)
        return entry
    
    def get_entries(self, student_id):
        """
        Get all journal entries for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            list: List of journal entries
        """
        return self.entries.get(student_id, [])
    
    def get_latest_entry(self, student_id):
        """
        Get the most recent journal entry for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            dict: The most recent journal entry or None if no entries exist
        """
        entries = self.get_entries(student_id)
        return entries[-1] if entries else None
    
    def _get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.datetime.utcnow().isoformat() + "Z"


class EmotionDetector:
    """Detector for emotional states in journal entries."""
    
    def __init__(self):
        self.sentiment_evaluator = SentimentEvaluator()
        self.uncertainty_evaluator = UncertaintyEvaluator()
        self.agitation_evaluator = AgitationEvaluator()
    
    def detect_uncertainty(self, text):
        """
        Detect level of uncertainty in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: Uncertainty score (0-100, where 0 is completely uncertain)
        """
        # Create a mock entry
        entry = {"text": text}
        return self.uncertainty_evaluator.evaluate(entry)
    
    def detect_agitation(self, text):
        """
        Detect level of agitation in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            float: Agitation score (0-100, where 0 is highly agitated)
        """
        # Create a mock entry
        entry = {"text": text}
        return self.agitation_evaluator.evaluate(entry)
    
    def get_emotional_state(self, text):
        """
        Get overall emotional state from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Emotional state analysis
        """
        # Create a mock entry
        entry = {"text": text}
        
        sentiment_score = self.sentiment_evaluator.evaluate(entry)
        uncertainty_score = self.uncertainty_evaluator.evaluate(entry)
        agitation_score = self.agitation_evaluator.evaluate(entry)
        
        # Determine if a halt is recommended
        halt_recommended = (
            uncertainty_score < 30 or
            agitation_score < 30
        )
        
        return {
            "sentiment_score": sentiment_score,
            "uncertainty_score": uncertainty_score,
            "agitation_score": agitation_score,
            "summary": self._generate_summary(sentiment_score, uncertainty_score, agitation_score),
            "halt_recommended": halt_recommended
        }
    
    def _generate_summary(self, sentiment_score, uncertainty_score, agitation_score):
        """Generate a summary explanation based on component scores."""
        if agitation_score < 30:
            return "Your journal entry indicates significant agitation. Consider taking a break before making decisions."
        elif uncertainty_score < 30:
            return "Your journal entry shows high uncertainty. It might help to discuss your concerns with a counselor."
        elif sentiment_score < 30:
            return "Your journal entry reflects negative emotions. Consider exploring these feelings further."
        else:
            return "Your emotional state appears balanced for decision-making."


class CounselingWrapper:
    """Wrapper for college counseling functionality."""
    
    def __init__(self, data_source_manager):
        self.data_source_manager = data_source_manager
        self.trust_framework = TrustEvaluationFramework()
        self.journal_manager = JournalManager()
        self.emotion_detector = EmotionDetector()
        self.governance_core = GovernanceCore()
        self.audit_trail = []
    
    def analyze_emotional_state(self, text):
        """
        Analyze emotional state from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Emotional state analysis
        """
        return self.emotion_detector.get_emotional_state(text)
    
    def generate_recommendations(self, student_profile, journal_entries=None):
        """
        Generate college recommendations for a student.
        
        Args:
            student_profile: Dictionary containing student data
            journal_entries: List of journal entries (optional)
            
        Returns:
            list: List of college recommendations with trust scores
        """
        # Get colleges from data source
        data_source = self.data_source_manager.get_data_source('mock')
        colleges = data_source.get_colleges(limit=10)
        
        # Evaluate each college
        recommendations = []
        
        for college in colleges:
            # Evaluate trust factors
            evaluation = self.trust_framework.evaluate(
                student_profile, college, journal_entries
            )
            
            # Add to recommendations
            recommendations.append({
                "college": college,
                "trust_score": evaluation["overall_score"],
                "category": evaluation["category"],
                "factors": evaluation["factors"],
                "halt_recommended": evaluation["halt_recommended"]
            })
        
        # Sort by trust score (descending)
        recommendations.sort(key=lambda x: x["trust_score"], reverse=True)
        
        # Record in audit trail
        self.record_recommendations(student_profile["id"], recommendations)
        
        return recommendations
    
    def record_recommendations(self, student_id, recommendations):
        """
        Record recommendations in audit trail.
        
        Args:
            student_id: ID of the student
            recommendations: List of recommendations
        """
        entry = {
            "type": "recommendations",
            "student_id": student_id,
            "timestamp": self.get_timestamp(),
            "recommendations": [
                {
                    "college_id": rec["college"]["id"],
                    "trust_score": rec["trust_score"],
                    "category": rec["category"],
                    "halt_recommended": rec["halt_recommended"]
                }
                for rec in recommendations
            ]
        }
        
        # Add to audit trail
        self.audit_trail.append(entry)
    
    def record_override(self, student_id, college_id, override):
        """
        Record override in audit trail.
        
        Args:
            student_id: ID of the student
            college_id: ID of the college
            override: Override data
        """
        entry = {
            "type": "override",
            "student_id": student_id,
            "college_id": college_id,
            "timestamp": self.get_timestamp(),
            "action": override["action"],
            "justification": override["justification"]
        }
        
        # Add to audit trail
        self.audit_trail.append(entry)
    
    def generate_report(self, student, journal_entries, recommendations, overrides):
        """
        Generate a comprehensive report.
        
        Args:
            student: Dictionary containing student data
            journal_entries: List of journal entries
            recommendations: List of recommendations
            overrides: List of overrides
            
        Returns:
            dict: Report data
        """
        # Extract emotional state summary
        emotional_state_summary = None
        if journal_entries:
            latest_entry = journal_entries[-1]
            if "emotional_state" in latest_entry:
                emotional_state_summary = latest_entry["emotional_state"]
        
        # Create report
        report = {
            "student": student,
            "generated_at": self.get_timestamp(),
            "emotional_state_summary": emotional_state_summary,
            "recommendations": recommendations,
            "overrides": overrides,
            "audit_trail": self.audit_trail
        }
        
        return report
    
    def get_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.datetime.utcnow().isoformat() + "Z"
