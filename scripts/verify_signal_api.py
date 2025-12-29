
import sys
import json
import urllib.request
import urllib.error

def test_api():
    url = "http://127.0.0.1:8000/signals/history?days=30&limit=10"
    print(f"🚀 Calling API: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ API Response 200 OK")
                signals = data.get('signals', [])
                print(f"📦 Received {len(signals)} signals")
                
                for s in signals:
                    symbol = s.get('symbol', 'UNK')
                    sig_type = s.get('signal_type', 'UNK')
                    print(f"   - {s.get('id')} ({symbol} {sig_type})")
                    
                # Check for TEST signal
                found = any(str(s.get('id')).startswith("TEST-") for s in signals)
                if found:
                    print("✅ TEST Signal FOUND in API response!")
                else:
                    print("❌ TEST Signal NOT FOUND (Persistence or API issue?)")
            else:
                print(f"❌ API Error {response.status}")

    except urllib.error.URLError as e:
        print(f"❌ Connection Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
