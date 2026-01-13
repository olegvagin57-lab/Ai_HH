"""
Comprehensive QA Test Suite for HH Resume Analyzer
Tests all critical functionality as a senior QA engineer would
"""
import asyncio
import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Test results storage
test_results: List[Dict[str, Any]] = []


def log_test(test_name: str, status: str, message: str = "", details: Any = None):
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    status_symbol = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    print(f"{status_symbol} {test_name}: {message}")


async def test_1_imports():
    """Test 1: Check all critical imports"""
    print("\n=== Test 1: Module Imports ===")
    
    try:
        from app.config import settings
        log_test("Config Import", "PASS", "Settings loaded successfully")
    except Exception as e:
        log_test("Config Import", "FAIL", f"Failed: {e}")
        return False
    
    try:
        from app.core.security import security_service
        log_test("Security Import", "PASS", "Security service loaded")
    except Exception as e:
        log_test("Security Import", "FAIL", f"Failed: {e}")
        return False
    
    try:
        from app.domain.entities.user import User, Role, Permission
        log_test("Domain Entities Import", "PASS", "Domain entities loaded")
    except Exception as e:
        log_test("Domain Entities Import", "FAIL", f"Failed: {e}")
        return False
    
    try:
        from app.application.services.auth_service import AuthService
        log_test("Auth Service Import", "PASS", "Auth service loaded")
    except Exception as e:
        log_test("Auth Service Import", "FAIL", f"Failed: {e}")
        return False
    
    try:
        from app.application.services.ai_service import ai_service
        log_test("AI Service Import", "PASS", "AI service loaded")
    except Exception as e:
        log_test("AI Service Import", "FAIL", f"Failed: {e}")
        return False
    
    return True


async def test_2_configuration():
    """Test 2: Configuration validation"""
    print("\n=== Test 2: Configuration ===")
    
    try:
        from app.config import settings
        
        # Check required settings
        if settings.mongodb_url:
            log_test("MongoDB URL", "PASS", f"Set to: {settings.mongodb_url[:30]}...")
        else:
            log_test("MongoDB URL", "FAIL", "Not configured")
        
        if settings.secret_key != "your-secret-key-here-change-in-production":
            log_test("Secret Key", "PASS", "Custom secret key set")
        else:
            log_test("Secret Key", "WARN", "Using default secret key (change in production)")
        
        log_test("Environment", "PASS", f"Environment: {settings.environment}")
        log_test("Debug Mode", "PASS", f"Debug: {settings.debug}")
        
        return True
    except Exception as e:
        log_test("Configuration", "FAIL", f"Failed: {e}")
        return False


async def test_3_security():
    """Test 3: Security functions"""
    print("\n=== Test 3: Security Functions ===")
    
    try:
        from app.core.security import security_service
        
        # Test password hashing (use shorter password to avoid bcrypt 72 byte limit)
        password = "Test123"
        try:
            hashed = security_service.get_password_hash(password)
            if hashed != password and len(hashed) > 0:
                log_test("Password Hashing", "PASS", "Password hashed successfully")
            else:
                log_test("Password Hashing", "FAIL", "Password not hashed")
                return False
        except Exception as e:
            log_test("Password Hashing", "FAIL", f"Failed: {e}")
            return False
        
        # Test password verification
        if security_service.verify_password(password, hashed):
            log_test("Password Verification", "PASS", "Password verified correctly")
        else:
            log_test("Password Verification", "FAIL", "Password verification failed")
            return False
        
        # Test password strength validation
        is_valid, message = security_service.validate_password_strength("weak")
        if not is_valid:
            log_test("Password Validation", "PASS", "Weak passwords rejected")
        else:
            log_test("Password Validation", "FAIL", "Weak password accepted")
            return False
        
        # Test JWT token creation
        token = security_service.create_access_token({"sub": "test_user"})
        if token:
            log_test("JWT Creation", "PASS", "Token created successfully")
        else:
            log_test("JWT Creation", "FAIL", "Token creation failed")
            return False
        
        # Test token verification
        payload = security_service.verify_token(token)
        if payload and payload.get("sub") == "test_user":
            log_test("JWT Verification", "PASS", "Token verified correctly")
        else:
            log_test("JWT Verification", "FAIL", "Token verification failed")
            return False
        
        return True
    except Exception as e:
        log_test("Security Functions", "FAIL", f"Failed: {e}")
        return False


async def test_4_ai_service():
    """Test 4: AI Service functionality"""
    print("\n=== Test 4: AI Service ===")
    
    try:
        from app.application.services.ai_service import ai_service
        
        # Test concept extraction
        concepts = await ai_service.extract_concepts("Python developer with FastAPI")
        if isinstance(concepts, list) and len(concepts) > 0:
            log_test("Concept Extraction", "PASS", f"Extracted {len(concepts)} concepts")
        else:
            log_test("Concept Extraction", "FAIL", "No concepts extracted")
            return False
        
        # Test resume analysis
        resume_text = "Senior Python Developer with 5 years experience in FastAPI"
        result = await ai_service.analyze_resume(resume_text, concepts)
        
        if "score" in result and 1 <= result["score"] <= 10:
            log_test("Resume Analysis", "PASS", f"Score: {result['score']}/10")
        else:
            log_test("Resume Analysis", "FAIL", "Invalid score returned")
            return False
        
        if "summary" in result and result["summary"]:
            log_test("AI Summary", "PASS", "Summary generated")
        else:
            log_test("AI Summary", "FAIL", "No summary generated")
            return False
        
        return True
    except Exception as e:
        log_test("AI Service", "FAIL", f"Failed: {e}")
        return False


async def test_5_database_models():
    """Test 5: Database models structure"""
    print("\n=== Test 5: Database Models ===")
    
    try:
        from app.domain.entities.user import User, Role, Permission
        from app.domain.entities.search import Search, Resume, Concept
        
        # Check User model
        user_fields = User.model_fields.keys()
        required_fields = ["email", "username", "hashed_password", "is_active"]
        if all(field in user_fields for field in required_fields):
            log_test("User Model", "PASS", "All required fields present")
        else:
            log_test("User Model", "FAIL", "Missing required fields")
            return False
        
        # Check Search model
        search_fields = Search.model_fields.keys()
        required_fields = ["user_id", "query", "city", "status"]
        if all(field in search_fields for field in required_fields):
            log_test("Search Model", "PASS", "All required fields present")
        else:
            log_test("Search Model", "FAIL", "Missing required fields")
            return False
        
        # Check Resume model
        resume_fields = Resume.model_fields.keys()
        required_fields = ["search_id", "preliminary_score", "ai_score"]
        if all(field in resume_fields for field in required_fields):
            log_test("Resume Model", "PASS", "All required fields present")
        else:
            log_test("Resume Model", "FAIL", "Missing required fields")
            return False
        
        return True
    except Exception as e:
        log_test("Database Models", "FAIL", f"Failed: {e}")
        return False


async def test_6_api_structure():
    """Test 6: API structure and routes"""
    print("\n=== Test 6: API Structure ===")
    
    try:
        from app.main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods)
                })
        
        # Check critical endpoints
        required_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/search",
            "/api/v1/health"
        ]
        
        route_paths = [r["path"] for r in routes]
        found_endpoints = []
        for endpoint in required_endpoints:
            if any(endpoint in path for path in route_paths):
                found_endpoints.append(endpoint)
                log_test(f"Endpoint: {endpoint}", "PASS", "Route exists")
            else:
                log_test(f"Endpoint: {endpoint}", "FAIL", "Route not found")
        
        if len(found_endpoints) == len(required_endpoints):
            return True
        else:
            return False
        
    except Exception as e:
        log_test("API Structure", "FAIL", f"Failed: {e}")
        return False


async def test_7_error_handling():
    """Test 7: Error handling"""
    print("\n=== Test 7: Error Handling ===")
    
    try:
        from app.core.exceptions import (
            AppException,
            ValidationException,
            NotFoundException,
            UnauthorizedException,
            ForbiddenException
        )
        
        # Test exception hierarchy
        exceptions = [
            ("AppException", AppException),
            ("ValidationException", ValidationException),
            ("NotFoundException", NotFoundException),
            ("UnauthorizedException", UnauthorizedException),
            ("ForbiddenException", ForbiddenException)
        ]
        
        for name, exc_class in exceptions:
            if issubclass(exc_class, AppException):
                log_test(f"Exception: {name}", "PASS", "Properly inherits from AppException")
            else:
                log_test(f"Exception: {name}", "FAIL", "Does not inherit from AppException")
                return False
        
        return True
    except Exception as e:
        log_test("Error Handling", "FAIL", f"Failed: {e}")
        return False


def generate_report():
    """Generate test report"""
    print("\n" + "=" * 50)
    print("QA TEST REPORT")
    print("=" * 50)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    warnings = sum(1 for r in test_results if r["status"] == "WARN")
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Warnings: {warnings}")
    
    if failed > 0:
        print("\nFailed Tests:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  - {result['test']}: {result['message']}")
    
    # Save report to file
    report_file = f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings
            },
            "tests": test_results
        }, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return failed == 0


async def main():
    """Run all tests"""
    print("=" * 50)
    print("HH RESUME ANALYZER - QA TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_1_imports),
        ("Configuration", test_2_configuration),
        ("Security Functions", test_3_security),
        ("AI Service", test_4_ai_service),
        ("Database Models", test_5_database_models),
        ("API Structure", test_6_api_structure),
        ("Error Handling", test_7_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            log_test(name, "FAIL", f"Test crashed: {e}")
            results.append(False)
    
    # Generate report
    all_passed = generate_report()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
