from database.connection_db import calculate_total
import sys

def test_parsing():
    print("Testing Currency Parsing...")
    
    data = {
        "janeiro": " R$ 1.248,81 ", # 1248.81
        "fevereiro": " R$ 557,64 ", # 557.64
        "marco": "3.312,00",        # 3312.00
        "abril": "0",
        "maio": "",
        "junho": None,
        "julho": 100.50             # Float check
    }
    
    # Expected: 1248.81 + 557.64 + 3312.00 + 0 + 0 + 0 + 100.50 = 5218.95
    expected = 5218.95
    
    result = calculate_total(data)
    print(f"Calculated: {result}, Expected: {expected}")
    
    if abs(result - expected) < 0.01:
        print("SUCCESS: Parsing logic works.")
    else:
        print("FAIL: Parsing logic incorrect.")
        sys.exit(1)

if __name__ == "__main__":
    test_parsing()
