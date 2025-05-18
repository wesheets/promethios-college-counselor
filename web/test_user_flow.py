"""
User flow testing script for College Counselor application.

This script tests the core user flow: profile update, journaling, and college recommendations.
"""

import os
import sys
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "student"
TEST_PASSWORD = "password"

def setup_webdriver():
    """Set up headless Chrome webdriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def test_login(driver):
    """Test user login functionality."""
    print("Testing login...")
    
    try:
        # Navigate to login page
        driver.get(f"{BASE_URL}/auth/login")
        
        # Fill in login form
        driver.find_element(By.ID, "username").send_keys(TEST_USERNAME)
        driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Check if login was successful
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-nav .nav-link"))
        )
        
        # Verify we're on the profile page or home page
        current_url = driver.current_url
        if "/profile" in current_url or current_url == f"{BASE_URL}/":
            print("✓ Login successful")
            return True
        else:
            print(f"✗ Login failed: Unexpected redirect to {current_url}")
            return False
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        return False

def test_profile_update(driver):
    """Test profile update functionality."""
    print("Testing profile update...")
    
    try:
        # Navigate to profile page
        driver.get(f"{BASE_URL}/profile")
        
        # Fill in profile form
        driver.find_element(By.ID, "gpa").clear()
        driver.find_element(By.ID, "gpa").send_keys("3.8")
        
        driver.find_element(By.ID, "graduation_year").clear()
        driver.find_element(By.ID, "graduation_year").send_keys("2026")
        
        driver.find_element(By.ID, "intended_majors").clear()
        driver.find_element(By.ID, "intended_majors").send_keys("Computer Science, Mathematics")
        
        driver.find_element(By.ID, "location_preference").clear()
        driver.find_element(By.ID, "location_preference").send_keys("California")
        
        driver.find_element(By.ID, "budget").clear()
        driver.find_element(By.ID, "budget").send_keys("50000")
        
        # Select dropdown options
        driver.find_element(By.ID, "size_preference").click()
        driver.find_element(By.CSS_SELECTOR, "#size_preference option[value='medium']").click()
        
        driver.find_element(By.ID, "setting_preference").click()
        driver.find_element(By.CSS_SELECTOR, "#setting_preference option[value='urban']").click()
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Check for success message
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        
        if "Profile updated successfully" in success_message.text:
            print("✓ Profile update successful")
            return True
        else:
            print(f"✗ Profile update failed: Unexpected message: {success_message.text}")
            return False
    except Exception as e:
        print(f"✗ Profile update test failed: {e}")
        return False

def test_journal_entry(driver):
    """Test journal entry creation."""
    print("Testing journal entry creation...")
    
    try:
        # Navigate to journal page
        driver.get(f"{BASE_URL}/journal")
        
        # Click on new entry button
        driver.find_element(By.CSS_SELECTOR, "a[href*='journal/new']").click()
        
        # Fill in journal entry form
        driver.find_element(By.ID, "title").send_keys("Test Journal Entry")
        driver.find_element(By.ID, "content").send_keys(
            "This is a test journal entry to validate the user flow. "
            "I'm feeling excited about the college application process, "
            "but also a bit nervous about making the right choice. "
            "I'm particularly interested in schools with strong computer science programs."
        )
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Check for success message
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        
        if "Journal entry saved successfully" in success_message.text:
            print("✓ Journal entry creation successful")
            
            # Check if entry appears in journal list
            entries = driver.find_elements(By.CSS_SELECTOR, ".journal-entry")
            if any("Test Journal Entry" in entry.text for entry in entries):
                print("✓ Journal entry appears in list")
                return True
            else:
                print("✗ Journal entry not found in list")
                return False
        else:
            print(f"✗ Journal entry creation failed: Unexpected message: {success_message.text}")
            return False
    except Exception as e:
        print(f"✗ Journal entry test failed: {e}")
        return False

def test_college_recommendations(driver):
    """Test college recommendations page."""
    print("Testing college recommendations...")
    
    try:
        # Navigate to colleges page
        driver.get(f"{BASE_URL}/colleges")
        
        # Check if college recommendations are displayed
        colleges = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".college-card"))
        )
        
        if len(colleges) > 0:
            print(f"✓ College recommendations displayed ({len(colleges)} colleges)")
            
            # Click on first college to test details page
            colleges[0].find_element(By.CSS_SELECTOR, "a").click()
            
            # Check if college details page loads
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".college-details-section"))
            )
            
            # Check for trust score
            trust_score = driver.find_element(By.CSS_SELECTOR, ".trust-score-circle")
            if trust_score:
                print(f"✓ College details page loaded with trust score: {trust_score.text}")
                return True
            else:
                print("✗ Trust score not found on college details page")
                return False
        else:
            print("✗ No college recommendations displayed")
            return False
    except Exception as e:
        print(f"✗ College recommendations test failed: {e}")
        return False

def test_report_generation(driver):
    """Test report generation."""
    print("Testing report generation...")
    
    try:
        # Navigate to report page
        driver.get(f"{BASE_URL}/report")
        
        # Check if report sections are displayed
        sections = [
            "student-profile-summary",
            "emotional-state-analysis",
            "recommendation-summary",
            "decision-trail"
        ]
        
        all_sections_present = True
        for section in sections:
            try:
                driver.find_element(By.ID, section)
            except NoSuchElementException:
                print(f"✗ Report section '{section}' not found")
                all_sections_present = False
        
        if all_sections_present:
            print("✓ Report generated successfully with all sections")
            return True
        else:
            print("✗ Some report sections are missing")
            return False
    except Exception as e:
        print(f"✗ Report generation test failed: {e}")
        return False

def test_logout(driver):
    """Test user logout functionality."""
    print("Testing logout...")
    
    try:
        # Click on logout link
        driver.find_element(By.CSS_SELECTOR, "a[href*='logout']").click()
        
        # Check if we're redirected to login page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        if "/login" in driver.current_url:
            print("✓ Logout successful")
            return True
        else:
            print(f"✗ Logout failed: Unexpected redirect to {driver.current_url}")
            return False
    except Exception as e:
        print(f"✗ Logout test failed: {e}")
        return False

def run_all_tests():
    """Run all user flow tests."""
    print("Starting user flow tests...")
    print("-" * 50)
    
    driver = setup_webdriver()
    
    try:
        # Run tests
        login_success = test_login(driver)
        if not login_success:
            print("✗ Login failed, skipping remaining tests")
            return False
        
        profile_success = test_profile_update(driver)
        journal_success = test_journal_entry(driver)
        recommendations_success = test_college_recommendations(driver)
        report_success = test_report_generation(driver)
        logout_success = test_logout(driver)
        
        # Summary
        print("-" * 50)
        print("\nUser Flow Test Summary:")
        print(f"Login: {'✓ Pass' if login_success else '✗ Fail'}")
        print(f"Profile Update: {'✓ Pass' if profile_success else '✗ Fail'}")
        print(f"Journal Entry: {'✓ Pass' if journal_success else '✗ Fail'}")
        print(f"College Recommendations: {'✓ Pass' if recommendations_success else '✗ Fail'}")
        print(f"Report Generation: {'✓ Pass' if report_success else '✗ Fail'}")
        print(f"Logout: {'✓ Pass' if logout_success else '✗ Fail'}")
        
        all_passed = (login_success and profile_success and journal_success and 
                      recommendations_success and report_success and logout_success)
        
        if all_passed:
            print("\n✓ All user flow tests passed successfully!")
        else:
            print("\n✗ Some user flow tests failed. See details above.")
        
        return all_passed
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
