"""
College Data Loader - Data Source Management

This module implements the data source management for college data,
including the College Scorecard API connector and mock data source.
"""

import json
import random
import datetime

class MockDataSource:
    """Mock data source for college data."""
    
    def __init__(self):
        # Sample college data for testing
        self.colleges = [
            {
                "id": "1",
                "name": "Ivy University",
                "location": {
                    "city": "Cambridge",
                    "state": "MA",
                    "zip": "02138"
                },
                "website": "https://www.ivy.edu",
                "admission_rate": 0.05,
                "average_gpa": 4.0,
                "cost": {
                    "tuition": 55000,
                    "room_and_board": 18000,
                    "books": 1200,
                    "total": 74200
                },
                "financial_aid": {
                    "average_package": 45000,
                    "percent_receiving_aid": 60
                },
                "majors": [
                    "Computer Science",
                    "Economics",
                    "Biology",
                    "Engineering",
                    "Mathematics"
                ],
                "enrollment": 20000,
                "campus_setting": "urban"
            },
            {
                "id": "2",
                "name": "State University",
                "location": {
                    "city": "Stateville",
                    "state": "CA",
                    "zip": "90210"
                },
                "website": "https://www.stateuniversity.edu",
                "admission_rate": 0.65,
                "average_gpa": 3.5,
                "cost": {
                    "tuition": 15000,
                    "room_and_board": 12000,
                    "books": 1000,
                    "total": 28000
                },
                "financial_aid": {
                    "average_package": 12000,
                    "percent_receiving_aid": 75
                },
                "majors": [
                    "Business",
                    "Psychology",
                    "Communications",
                    "Computer Science",
                    "Biology"
                ],
                "enrollment": 35000,
                "campus_setting": "suburban"
            },
            {
                "id": "3",
                "name": "Liberal Arts College",
                "location": {
                    "city": "Smalltown",
                    "state": "VT",
                    "zip": "05401"
                },
                "website": "https://www.liberalarts.edu",
                "admission_rate": 0.25,
                "average_gpa": 3.8,
                "cost": {
                    "tuition": 45000,
                    "room_and_board": 14000,
                    "books": 1100,
                    "total": 60100
                },
                "financial_aid": {
                    "average_package": 35000,
                    "percent_receiving_aid": 80
                },
                "majors": [
                    "English",
                    "Philosophy",
                    "History",
                    "Art",
                    "Political Science"
                ],
                "enrollment": 2500,
                "campus_setting": "rural"
            },
            {
                "id": "4",
                "name": "Tech Institute",
                "location": {
                    "city": "Techville",
                    "state": "WA",
                    "zip": "98101"
                },
                "website": "https://www.techinstitute.edu",
                "admission_rate": 0.15,
                "average_gpa": 3.9,
                "cost": {
                    "tuition": 50000,
                    "room_and_board": 16000,
                    "books": 1500,
                    "total": 67500
                },
                "financial_aid": {
                    "average_package": 30000,
                    "percent_receiving_aid": 70
                },
                "majors": [
                    "Computer Science",
                    "Electrical Engineering",
                    "Mechanical Engineering",
                    "Data Science",
                    "Robotics"
                ],
                "enrollment": 15000,
                "campus_setting": "urban"
            },
            {
                "id": "5",
                "name": "Community College",
                "location": {
                    "city": "Hometown",
                    "state": "TX",
                    "zip": "75001"
                },
                "website": "https://www.communitycollege.edu",
                "admission_rate": 0.95,
                "average_gpa": 2.8,
                "cost": {
                    "tuition": 5000,
                    "room_and_board": 0,
                    "books": 800,
                    "total": 5800
                },
                "financial_aid": {
                    "average_package": 3000,
                    "percent_receiving_aid": 85
                },
                "majors": [
                    "Business",
                    "Nursing",
                    "Computer Science",
                    "Education",
                    "Criminal Justice"
                ],
                "enrollment": 8000,
                "campus_setting": "suburban"
            },
            {
                "id": "6",
                "name": "Arts Academy",
                "location": {
                    "city": "Artsville",
                    "state": "NY",
                    "zip": "10001"
                },
                "website": "https://www.artsacademy.edu",
                "admission_rate": 0.20,
                "average_gpa": 3.7,
                "cost": {
                    "tuition": 48000,
                    "room_and_board": 15000,
                    "books": 2000,
                    "total": 65000
                },
                "financial_aid": {
                    "average_package": 25000,
                    "percent_receiving_aid": 65
                },
                "majors": [
                    "Fine Arts",
                    "Music",
                    "Theater",
                    "Dance",
                    "Film"
                ],
                "enrollment": 3000,
                "campus_setting": "urban"
            },
            {
                "id": "7",
                "name": "Midwest University",
                "location": {
                    "city": "Centreville",
                    "state": "IL",
                    "zip": "60601"
                },
                "website": "https://www.midwestuniversity.edu",
                "admission_rate": 0.45,
                "average_gpa": 3.4,
                "cost": {
                    "tuition": 35000,
                    "room_and_board": 12000,
                    "books": 1000,
                    "total": 48000
                },
                "financial_aid": {
                    "average_package": 20000,
                    "percent_receiving_aid": 75
                },
                "majors": [
                    "Business",
                    "Engineering",
                    "Agriculture",
                    "Education",
                    "Nursing"
                ],
                "enrollment": 25000,
                "campus_setting": "suburban"
            },
            {
                "id": "8",
                "name": "Southern College",
                "location": {
                    "city": "Southville",
                    "state": "GA",
                    "zip": "30301"
                },
                "website": "https://www.southerncollege.edu",
                "admission_rate": 0.55,
                "average_gpa": 3.3,
                "cost": {
                    "tuition": 30000,
                    "room_and_board": 11000,
                    "books": 900,
                    "total": 41900
                },
                "financial_aid": {
                    "average_package": 18000,
                    "percent_receiving_aid": 70
                },
                "majors": [
                    "Business",
                    "Communications",
                    "Psychology",
                    "Biology",
                    "History"
                ],
                "enrollment": 18000,
                "campus_setting": "suburban"
            },
            {
                "id": "9",
                "name": "Western University",
                "location": {
                    "city": "Westville",
                    "state": "CO",
                    "zip": "80201"
                },
                "website": "https://www.westernuniversity.edu",
                "admission_rate": 0.60,
                "average_gpa": 3.2,
                "cost": {
                    "tuition": 25000,
                    "room_and_board": 10000,
                    "books": 800,
                    "total": 35800
                },
                "financial_aid": {
                    "average_package": 15000,
                    "percent_receiving_aid": 65
                },
                "majors": [
                    "Environmental Science",
                    "Geology",
                    "Recreation Management",
                    "Wildlife Biology",
                    "Forestry"
                ],
                "enrollment": 12000,
                "campus_setting": "rural"
            },
            {
                "id": "10",
                "name": "Medical University",
                "location": {
                    "city": "Medville",
                    "state": "PA",
                    "zip": "19101"
                },
                "website": "https://www.medicaluniversity.edu",
                "admission_rate": 0.10,
                "average_gpa": 3.9,
                "cost": {
                    "tuition": 60000,
                    "room_and_board": 15000,
                    "books": 2000,
                    "total": 77000
                },
                "financial_aid": {
                    "average_package": 35000,
                    "percent_receiving_aid": 60
                },
                "majors": [
                    "Medicine",
                    "Nursing",
                    "Pharmacy",
                    "Public Health",
                    "Biomedical Sciences"
                ],
                "enrollment": 5000,
                "campus_setting": "urban"
            }
        ]
    
    def get_colleges(self, limit=25):
        """
        Get a list of colleges.
        
        Args:
            limit: Maximum number of colleges to return
            
        Returns:
            list: List of college dictionaries
        """
        return self.colleges[:min(limit, len(self.colleges))]
    
    def get_college_by_id(self, college_id):
        """
        Get a specific college by ID.
        
        Args:
            college_id: ID of the college
            
        Returns:
            dict: College dictionary or None if not found
        """
        for college in self.colleges:
            if college["id"] == college_id:
                return college
        return None
    
    def search_colleges(self, query, limit=25):
        """
        Search for colleges by name or other criteria.
        
        Args:
            query: Search query
            limit: Maximum number of colleges to return
            
        Returns:
            list: List of college dictionaries
        """
        query = query.lower()
        results = []
        
        for college in self.colleges:
            if query in college["name"].lower():
                results.append(college)
            elif query in college["location"]["state"].lower():
                results.append(college)
            elif any(query in major.lower() for major in college["majors"]):
                results.append(college)
        
        return results[:min(limit, len(results))]


class CollegeScorecard:
    """Connector for College Scorecard API."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.api_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
        
        # For demo purposes, use mock data if no API key is provided
        self.mock_data_source = MockDataSource()
    
    def get_colleges(self, limit=25):
        """
        Get a list of colleges from the College Scorecard API.
        
        Args:
            limit: Maximum number of colleges to return
            
        Returns:
            list: List of college dictionaries
        """
        if not self.api_key:
            # Use mock data if no API key is provided
            return self.mock_data_source.get_colleges(limit)
        
        # In a real implementation, this would make an API request
        # For demo purposes, return mock data
        return self.mock_data_source.get_colleges(limit)
    
    def get_college_by_id(self, college_id):
        """
        Get a specific college by ID.
        
        Args:
            college_id: ID of the college
            
        Returns:
            dict: College dictionary or None if not found
        """
        if not self.api_key:
            # Use mock data if no API key is provided
            return self.mock_data_source.get_college_by_id(college_id)
        
        # In a real implementation, this would make an API request
        # For demo purposes, return mock data
        return self.mock_data_source.get_college_by_id(college_id)
    
    def search_colleges(self, query, limit=25):
        """
        Search for colleges by name or other criteria.
        
        Args:
            query: Search query
            limit: Maximum number of colleges to return
            
        Returns:
            list: List of college dictionaries
        """
        if not self.api_key:
            # Use mock data if no API key is provided
            return self.mock_data_source.search_colleges(query, limit)
        
        # In a real implementation, this would make an API request
        # For demo purposes, return mock data
        return self.mock_data_source.search_colleges(query, limit)


class DataSourceManager:
    """Manager for data sources."""
    
    def __init__(self):
        self.data_sources = {}
    
    def register_data_source(self, name, data_source):
        """
        Register a data source.
        
        Args:
            name: Name of the data source
            data_source: Data source object
        """
        self.data_sources[name] = data_source
    
    def get_data_source(self, name):
        """
        Get a data source by name.
        
        Args:
            name: Name of the data source
            
        Returns:
            object: Data source object or None if not found
        """
        return self.data_sources.get(name)
    
    def get_available_data_sources(self):
        """
        Get a list of available data sources.
        
        Returns:
            list: List of data source names
        """
        return list(self.data_sources.keys())
