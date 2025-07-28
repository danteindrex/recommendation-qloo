#!/usr/bin/env python3
"""
Verification script for CulturalOS development environment setup.
"""

import requests
import sys
import time

def test_backend_health():
    """Test backend health endpoint."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API: {data}")
            return True
        else:
            print(f"❌ Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API error: {e}")
        return False

def test_frontend():
    """Test frontend availability."""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Available")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def test_api_docs():
    """Test API documentation."""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Documentation: Available")
            return True
        else:
            print(f"❌ API docs returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints."""
    endpoints = [
        ("POST", "/api/auth/register"),
        ("GET", "/api/cultural/profile"), 
        ("GET", "/api/analytics/user"),
        ("GET", "/api/admin/platform-analytics")
    ]
    
    success_count = 0
    for method, endpoint in endpoints:
        try:
            if method == "POST":
                response = requests.post(f"http://localhost:8000{endpoint}", timeout=5)
            else:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            
            # We expect these to return 422 (validation error), 200, or 401 (auth required), not 404
            if response.status_code in [200, 401, 422]:
                print(f"✅ Endpoint {method} {endpoint}: Available")
                success_count += 1
            else:
                print(f"❌ Endpoint {method} {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Endpoint {method} {endpoint}: Error {e}")
    
    return success_count == len(endpoints)

def main():
    """Run all verification tests."""
    print("🚀 Verifying CulturalOS Development Environment Setup...")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend", test_frontend),
        ("API Documentation", test_api_docs),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your development environment is ready.")
        print("\n📋 Next steps:")
        print("1. Visit http://localhost:3000 for the frontend")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Start implementing your features!")
        return 0
    else:
        print("❌ Some tests failed. Please check the Docker containers:")
        print("   docker-compose logs")
        return 1

if __name__ == "__main__":
    sys.exit(main())