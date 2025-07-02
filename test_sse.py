# -*- coding: utf-8 -*-
import asyncio
import json
import requests
import time
from datetime import datetime

def test_health_endpoint():
    """Tests the health check endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"📊 Server: {data['server']} v{data['version']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sync_sse_endpoint(url: str, duration: int = 10):
    """Tests an SSE endpoint synchronously"""
    print(f"🧪 Testing {url} for {duration} seconds...")
    
    try:
        response = requests.get(
            url,
            stream=True,
            headers={
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            },
            timeout=30
        )
        response.raise_for_status()
        
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        start_time = time.time()
        event_count = 0
        
        for line in response.iter_lines(decode_unicode=True):
            if time.time() - start_time > duration:
                break
                
            if line and line.startswith('data: '):
                event_count += 1
                try:
                    data = json.loads(line[6:])  # Remove 'data: '
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message = data.get('message', 'N/A')
                    print(f"[{timestamp}] 📡 Event #{event_count}: {message}")
                except json.JSONDecodeError:
                    print(f"📄 Raw data: {line}")
        
        print(f"🏁 Test finished. Total events: {event_count}")
        return event_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_broadcast_api():
    """Tests the broadcast endpoint"""
    print("🧪 Testing broadcast API...")
    
    try:
        data = {
            "message": "Broadcast test from the test script",
            "timestamp": datetime.now().isoformat(),
            "sender": "test_script"
        }
        response = requests.post(
            "http://127.0.0.1:8000/api/broadcast",
            json=data,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Broadcast sent: {result['status']}")
        return True
    except Exception as e:
        print(f"❌ Error in broadcast: {e}")
        return False

def test_all_endpoints():
    """Runs all tests in sequence"""
    print("🚀 Starting FastAPI SSE test suite")
    print("=" * 50)
    
    # Health check test
    if not test_health_endpoint():
        print("⚠️  Server is not responding. Run: python main.py")
        return False
    
    print("\n" + "-" * 50)
    
    # Main stream test
    stream_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/stream", 5)
    
    print("\n" + "-" * 50)
    
    # Metrics stream test
    metrics_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/metrics", 5)
    
    print("\n" + "-" * 50)
    
    # Custom channel test
    channel_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/realtime/test", 5)
    
    print("\n" + "-" * 50)
    
    # Broadcast API test
    broadcast_ok = test_broadcast_api()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Health Check: {'✅' if True else '❌'}")
    print(f"   Main Stream: {'✅' if stream_ok else '❌'}")
    print(f"   Metrics: {'✅' if metrics_ok else '❌'}")
    print(f"   Custom Channel: {'✅' if channel_ok else '❌'}")
    print(f"   Broadcast API: {'✅' if broadcast_ok else '❌'}")
    
    all_ok = stream_ok and metrics_ok and channel_ok and broadcast_ok
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_ok else '❌ SOME TESTS FAILED'}")
    
    return all_ok

def interactive_test():
    """Interactive test to choose specific endpoints"""
    print("🚀 FastAPI SSE - Interactive Test")
    print("=" * 40)
    print("1. Health Check")
    print("2. Main Stream (/stream)")
    print("3. Metrics (/metrics)")
    print("4. Custom Channel (/realtime/test)")
    print("5. Broadcast API")
    print("6. Run All Tests")
    print("7. Exit")
    print("=" * 40)
    
    while True:
        try:
            choice = input("\nChoose an option (1-7): ").strip()
            
            if choice == '1':
                test_health_endpoint()
            elif choice == '2':
                test_sync_sse_endpoint("http://127.0.0.1:8000/stream", 10)
            elif choice == '3':
                test_sync_sse_endpoint("http://127.0.0.1:8000/metrics", 10)
            elif choice == '4':
                test_sync_sse_endpoint("http://127.0.0.1:8000/realtime/test", 10)
            elif choice == '5':
                test_broadcast_api()
            elif choice == '6':
                test_all_endpoints()
            elif choice == '7':
                print("👋 Exiting tests...")
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except EOFError:
            print("\n👋 Exiting tests...")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automatic mode
        test_all_endpoints()
    else:
        # Interactive mode
        interactive_test()