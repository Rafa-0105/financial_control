import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def verify_total():
    # 1. Create a new expense with known values
    print("Testing Creation...")
    despesa_data = {
        "despesa": "Teste Total",
        "janeiro": "100.50",
        "fevereiro": "200.00"
    }
    # Expect total = 300.50
    
    response = requests.post(f"{BASE_URL}/despesas", json=despesa_data)
    if response.status_code != 201:
        print(f"Creation Failed: {response.text}")
        sys.exit(1)
        
    created = response.json()
    print(f"Created Expense: {json.dumps(created, indent=2)}")
    
    # Check structure
    if 'monthly_data' not in created or 'annual_total' not in created:
        print("FAIL: Response structure is incorrect (missing monthly_data or annual_total).")
        sys.exit(1)

    total_val = created['annual_total']
    if total_val != 300.50:
        print(f"FAIL: Total calculation on create is incorrect. Expected 300.50, got {total_val}")
        sys.exit(1)
        
    despesa_id = created['id']
    
    # 2. Update the expense (add march)
    print("\nTesting Update...")
    update_data = {
        "marco": "50.00"
    }
    # New Total Should be 350.50
    
    response = requests.put(f"{BASE_URL}/despesas/{despesa_id}", json=update_data)
    if response.status_code != 200:
        print(f"Update Failed: {response.text}")
        sys.exit(1)
        
    updated = response.json()
    print(f"Updated Expense: Annual Total = {updated.get('annual_total')}")
    
    if updated.get('annual_total') != 350.50:
        print("FAIL: Total calculation on update is incorrect.")
        sys.exit(1)

    print("\nSUCCESS: Total calculation verified.")

if __name__ == "__main__":
    try:
        verify_total()
    except Exception as e:
        print(f"Error: {e}")
