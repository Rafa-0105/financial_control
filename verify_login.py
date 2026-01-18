import requests
import sys

BASE_URL = "http://localhost:8000"

def test_workflow():
    # 1. Register User
    print("Testing Registration...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    # Try to register (might fail if already exists, which is fine)
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    
    if response.status_code == 201:
        print("Registration successful!")
    elif response.status_code == 400 and "already registered" in response.text:
        print("User already registered (Expected if running multiple times).")
    else:
        print(f"Registration Failed: {response.status_code} - {response.text}")
        sys.exit(1)

    # 2. Login
    print("\nTesting Login...")
    login_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        print("Login successful!")
        print("Response:", response.json())
    else:
        print(f"Login Failed: {response.status_code} - {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_workflow()
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is it running?")
