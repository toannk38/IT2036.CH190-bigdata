#!/usr/bin/env python3
"""
Verify that all required packages are installed correctly.
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def main():
    print("Verifying Python package installation...")
    print(f"Python version: {sys.version}")
    print()
    
    packages = [
        ("vnstock", "vnstock"),
        ("kafka-python", "kafka"),
        ("pymongo", "pymongo"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("apache-airflow", "airflow"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("ta", "ta"),
        ("openai", "openai"),
        ("anthropic", "anthropic"),
        ("pytest", "pytest"),
        ("hypothesis", "hypothesis"),
        ("python-dotenv", "dotenv"),
        ("requests", "requests"),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    print()
    if all(results):
        print("✓ All packages installed successfully!")
        return 0
    else:
        print("✗ Some packages are missing. Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
