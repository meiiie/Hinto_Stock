"""
Test script for Token Search and Add functionality
SOTA Phase 26b: Token Management API Tests

Run with: python scripts/test_token_api.py
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_token_search():
    """Test token search endpoint"""
    print("\n" + "="*50)
    print("TEST: Token Search API")
    print("="*50)
    
    # Test 1: Search for XRP
    print("\n[1] Searching for 'XRP'...")
    try:
        response = requests.get(f"{BASE_URL}/settings/tokens/search?q=XRP&limit=10", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data.get('total', 0)} symbols")
            print(f"   Symbols: {data.get('symbols', [])[:5]}...")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Search with empty query
    print("\n[2] Searching with empty query...")
    try:
        response = requests.get(f"{BASE_URL}/settings/tokens/search?q=&limit=5", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data.get('total', 0)} symbols (should be all USDT pairs)")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_token_validate():
    """Test token validation endpoint"""
    print("\n" + "="*50)
    print("TEST: Token Validate API")
    print("="*50)
    
    # Test 1: Valid symbol
    print("\n[1] Validating 'BTCUSDT' (valid)...")
    try:
        response = requests.get(f"{BASE_URL}/settings/tokens/validate?symbol=BTCUSDT", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Valid: {data.get('valid')}, Exists: {data.get('exists')}")
            if data.get('valid') and data.get('exists'):
                print("   ✅ PASSED")
            else:
                print("   ⚠️ UNEXPECTED RESULT")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Invalid symbol
    print("\n[2] Validating 'INVALIDCOIN' (invalid)...")
    try:
        response = requests.get(f"{BASE_URL}/settings/tokens/validate?symbol=INVALIDCOIN", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Valid: {data.get('valid')}, Exists: {data.get('exists')}")
            if not data.get('exists'):
                print("   ✅ PASSED (correctly identified as not existing)")
            else:
                print("   ⚠️ UNEXPECTED: Should not exist")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_token_add():
    """Test add token endpoint"""
    print("\n" + "="*50)
    print("TEST: Token Add API")
    print("="*50)
    
    # Test 1: Add valid token
    print("\n[1] Adding 'XLMUSDT'...")
    try:
        response = requests.post(
            f"{BASE_URL}/settings/tokens/add",
            json={"symbol": "XLMUSDT"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tokens count: {len(data.get('tokens', []))}")
            print("   ✅ PASSED")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Get current watchlist
    print("\n[2] Getting current watchlist...")
    try:
        response = requests.get(f"{BASE_URL}/settings/tokens", timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('tokens', [])
            print(f"   Total tokens: {len(tokens)}")
            for t in tokens[:5]:
                print(f"      - {t['symbol']}: {'Enabled' if t['enabled'] else 'Disabled'}")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def main():
    print("\n" + "="*60)
    print("TOKEN API TEST SUITE")
    print("="*60)
    print(f"Backend URL: {BASE_URL}")
    
    test_token_search()
    test_token_validate()
    test_token_add()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED")
    print("="*50)

if __name__ == "__main__":
    main()
