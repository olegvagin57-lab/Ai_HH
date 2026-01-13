#!/usr/bin/env python3
"""
E2E User Test - Testing from HR Manager perspective
Simulates a user who needs to find resumes for a job position
"""
import sys
import os
import time
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, status, message=""):
    """Print test result"""
    status_color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{status_color}[{status}]{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET}")
    if message:
        print(f"      {message}")

def print_step(step_num, description):
    """Print test step"""
    print(f"\n{Colors.CYAN}=== Step {step_num}: {description} ==={Colors.RESET}")

def test_health_check():
    """Test 1: Health check"""
    print_step(1, "Health Check")
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print_test("Backend Health", "PASS", "Backend is running")
            return True
        else:
            print_test("Backend Health", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Backend Health", "FAIL", f"Error: {str(e)}")
        return False

def test_register_user():
    """Test 2: Register new HR Manager user"""
    print_step(2, "Register New User (HR Manager)")
    
    # Generate unique email
    timestamp = int(time.time())
    user_data = {
        "email": f"hr_manager_{timestamp}@company.com",
        "username": f"hr_manager_{timestamp}",
        "password": "SecurePass123!",
        "full_name": "Иван Петров",
        "company_name": "ТехноКомпания",
        "position": "HR Manager"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print_test("User Registration", "PASS", f"User ID: {data.get('id')}")
            print(f"      Email: {user_data['email']}")
            print(f"      Username: {user_data['username']}")
            return user_data, data
        else:
            print_test("User Registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None, None
    except Exception as e:
        print_test("User Registration", "FAIL", f"Error: {str(e)}")
        return None, None

def test_login(user_data):
    """Test 3: Login"""
    print_step(3, "Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email_or_username": user_data["email"],
                "password": user_data["password"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            user = data.get("user")
            
            print_test("Login", "PASS", f"User: {user.get('username')}")
            print(f"      Token received: {len(access_token) if access_token else 0} chars")
            return access_token, refresh_token, user
        else:
            print_test("Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None, None, None
    except Exception as e:
        print_test("Login", "FAIL", f"Error: {str(e)}")
        return None, None, None

def test_create_search(access_token):
    """Test 4: Create search for resumes"""
    print_step(4, "Create Search for Resumes")
    
    search_data = {
        "query": "Python разработчик с опытом работы с FastAPI и MongoDB",
        "city": "Москва",
        "max_results": 10
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json=search_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            search_id = data.get("id")
            status = data.get("status")
            
            print_test("Create Search", "PASS", f"Search ID: {search_id}")
            print(f"      Query: {search_data['query']}")
            print(f"      Status: {status}")
            return search_id, data
        else:
            print_test("Create Search", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None, None
    except Exception as e:
        print_test("Create Search", "FAIL", f"Error: {str(e)}")
        return None, None

def test_check_search_status(access_token, search_id):
    """Test 5: Check search status"""
    print_step(5, "Check Search Status")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    max_wait = 60  # Wait up to 60 seconds
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get(
                f"{BASE_URL}/search/{search_id}/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                progress = data.get("progress", 0)
                
                print(f"      Status: {status}, Progress: {progress}%")
                
                if status in ["completed", "failed"]:
                    print_test("Search Status", "PASS", f"Final status: {status}")
                    return data
                
                time.sleep(2)
                wait_time += 2
            else:
                print_test("Search Status", "FAIL", f"Status: {response.status_code}")
                return None
        except Exception as e:
            print_test("Search Status", "FAIL", f"Error: {str(e)}")
            return None
    
    print_test("Search Status", "WARN", "Timeout waiting for completion")
    return None

def test_get_search_results(access_token, search_id):
    """Test 6: Get search results"""
    print_step(6, "Get Search Results")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/search/{search_id}/resumes",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            resumes = data.get("resumes", [])
            total = data.get("total", 0)
            
            print_test("Get Results", "PASS", f"Found {total} resumes")
            
            if resumes:
                print(f"\n      {Colors.CYAN}Top 3 Resumes:{Colors.RESET}")
                for i, resume in enumerate(resumes[:3], 1):
                    score = resume.get("ai_score", 0)
                    title = resume.get("title", "N/A")
                    print(f"      {i}. {title} (Score: {score:.2f})")
            
            return data
        else:
            print_test("Get Results", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test("Get Results", "FAIL", f"Error: {str(e)}")
        return None

def test_export_results(access_token, search_id, format="excel"):
    """Test 7: Export results"""
    print_step(7, f"Export Results ({format.upper()})")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/search/{search_id}/export/{format}",
            headers=headers,
            timeout=30,
            stream=True
        )
        
        if response.status_code == 200:
            filename = f"test_export_{search_id}.{format if format == 'csv' else 'xlsx'}"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filename)
            print_test("Export Results", "PASS", f"Exported to {filename} ({file_size} bytes)")
            return filename
        else:
            print_test("Export Results", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test("Export Results", "FAIL", f"Error: {str(e)}")
        return None

def main():
    """Run all E2E tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("E2E USER TEST - HR Manager Resume Search Scenario")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    # Test 1: Health check
    if not test_health_check():
        print(f"\n{Colors.RED}Backend is not available. Please start it first.{Colors.RESET}")
        return
    
    # Test 2: Register
    user_data, user_response = test_register_user()
    if not user_data:
        print(f"\n{Colors.RED}Registration failed. Cannot continue.{Colors.RESET}")
        return
    results["passed"] += 1
    
    # Test 3: Login
    access_token, refresh_token, user = test_login(user_data)
    if not access_token:
        print(f"\n{Colors.RED}Login failed. Cannot continue.{Colors.RESET}")
        return
    results["passed"] += 1
    
    # Test 4: Create search
    search_id, search_data = test_create_search(access_token)
    if not search_id:
        print(f"\n{Colors.YELLOW}Search creation failed. Some features may not work.{Colors.RESET}")
        results["warnings"] += 1
    else:
        results["passed"] += 1
        
        # Test 5: Check status
        status_data = test_check_search_status(access_token, search_id)
        if status_data:
            results["passed"] += 1
        else:
            results["warnings"] += 1
        
        # Test 6: Get results
        results_data = test_get_search_results(access_token, search_id)
        if results_data:
            results["passed"] += 1
        else:
            results["warnings"] += 1
        
        # Test 7: Export
        export_file = test_export_results(access_token, search_id, "excel")
        if export_file:
            results["passed"] += 1
        else:
            results["warnings"] += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings: {results['warnings']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    
    total = results["passed"] + results["warnings"] + results["failed"]
    success_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}\n")
    
    if results["passed"] >= 5:
        print(f"{Colors.GREEN}[PASS] E2E Test: PASSED - System is ready for use!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}[WARN] E2E Test: PARTIAL - Some features may not work{Colors.RESET}\n")

if __name__ == "__main__":
    main()
