"""Script to check project setup and dependencies"""
import sys
import importlib


def check_import(module_name, package_name=None):
    """Check if module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"[OK] {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {package_name or module_name}: {e}")
        return False


def main():
    """Check all required dependencies"""
    print("Checking Python dependencies...")
    print("-" * 50)
    
    required = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("motor", "Motor (MongoDB)"),
        ("beanie", "Beanie"),
        ("redis", "Redis"),
        ("celery", "Celery"),
        ("jose", "python-jose"),
        ("passlib", "Passlib"),
        ("httpx", "HTTPX"),
        ("openpyxl", "OpenPyXL"),
        ("structlog", "Structlog"),
        ("prometheus_client", "Prometheus Client"),
    ]
    
    results = []
    for module, name in required:
        results.append(check_import(module, name))
    
    print("-" * 50)
    
    if all(results):
        print("[OK] All dependencies are installed!")
        return 0
    else:
        print("[FAIL] Some dependencies are missing. Run: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
