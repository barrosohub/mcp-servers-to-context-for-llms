# -*- coding: utf-8 -*-
import requests
import json
import time
import threading
import signal
import sys
from typing import Optional

class FastAPISSEClient:
    """Python client to consume Server-Sent Events from FastAPI"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.connections = {}
        self.running = False
        
    def connect(self, endpoint: str, callback=None):
        """Connects to a specific SSE endpoint"""
        url = f"{self.base_url}{endpoint}"
        self.running = True
        
        try:
            print(f"🔗 Connecting to {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Connected to {endpoint}")
            
            for line in response.iter_lines(decode_unicode=True):
                if not self.running:
                    break
                    
                if line:
                    try:
                        # Parse SSE line
                        if line.startswith('data: '):
                            event_data = line[6:]  # Remove 'data: '
                            event = {'event': 'message', 'data': event_data}
                        elif line.startswith('event: '):
                            event_type = line[7:]  # Remove 'event: '
                            continue  # Wait for the next line with data
                        else:
                            continue
                            
                        if callback:
                            callback(event)
                        else:
                            self._default_handler(event, endpoint)
                            
                    except KeyboardInterrupt:
                        print("\n⚠️  Interrupted by user")
                        break
                    except Exception as e:
                        print(f"❌ Error processing event: {e}")
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.running = False
            print(f"🔌 Disconnected from {endpoint}")
    
    def _default_handler(self, event, endpoint):
        """Default handler for SSE events"""
        timestamp = time.strftime("%H:%M:%S")
        
        try:
            data = json.loads(event['data'])
            
            if event.get('event') == 'heartbeat':
                cpu = data.get('cpu_usage', 'N/A')
                memory = data.get('memory_usage', 'N/A')
                print(f"[{timestamp}] 💓 {endpoint} - CPU: {cpu}, Memory: {memory}")
                
            elif event.get('event') == 'notification':
                level = data.get('level', 'info')
                title = data.get('title', 'Notification')
                message = data.get('message', '')
                icon = {'info': 'ℹ️', 'warning': '⚠️', 'success': '✅', 'error': '❌'}.get(level, 'ℹ️')
                print(f"[{timestamp}] {icon} {title}: {message}")
                
            elif event.get('event') == 'sensor':
                sensor_data = data.get('sensor_data', {})
                temp = sensor_data.get('temperature', 'N/A')
                humidity = sensor_data.get('humidity', 'N/A')
                print(f"[{timestamp}] 🌡️  Sensor - Temp: {temp}°C, Humidity: {humidity}%")
                
            elif 'metrics' in data:
                metrics = data['metrics']
                rps = metrics.get('requests_per_second', 0)
                cpu_percent = metrics.get('cpu_usage_percent', 0)
                memory_mb = metrics.get('memory_usage_mb', 0)
                print(f"[{timestamp}] 📊 Metrics - RPS: {rps}, CPU: {cpu_percent}%, Mem: {memory_mb}MB")
                
            else:
                message = data.get('message', 'Data received')
                print(f"[{timestamp}] 📝 {endpoint} - {message}")
                
        except json.JSONDecodeError:
            print(f"[{timestamp}] 📄 {endpoint} - Raw: {event['data']}")
    
    def stop(self):
        """Stops all connections"""
        self.running = False

def test_health():
    """Tests the health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check OK: {data['status']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Client demonstration"""
    print("🚀 FastAPI SSE Client")
    print("=" * 40)
    
    # Test connection first
    if not test_health():
        print("⚠️  Server is not responding. Make sure it's running:")
        print("   python main.py")
        return
    
    print("1. Main Stream (/stream)")
    print("2. Metrics (/metrics)")
    print("3. Custom Channel (/realtime/demo)")
    print("4. Broadcast Test")
    print("5. Exit")
    print("=" * 40)
    
    client = FastAPISSEClient()
    
    while True:
        try:
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == '1':
                print("Connecting to the main stream...")
                client.connect('/stream')
            elif choice == '2':
                print("Connecting to metrics...")
                client.connect('/metrics')
            elif choice == '3':
                print("Connecting to the demo channel...")
                client.connect('/realtime/demo')
            elif choice == '4':
                print("Sending broadcast...")
                test_broadcast()
            elif choice == '5':
                print("👋 Exiting...")
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            client.stop()
            break
        except EOFError:
            print("\n👋 Exiting...")
            break

def test_broadcast():
    """Tests the broadcast endpoint"""
    try:
        data = {
            "message": "Broadcast test from Python client",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post("http://127.0.0.1:8000/api/broadcast", json=data, timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Broadcast sent: {result['status']}")
    except Exception as e:
        print(f"❌ Error in broadcast: {e}")

if __name__ == "__main__":
    # Handler for system signals
    def signal_handler(sig, frame):
        print('\n🛑 Signal received, exiting...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    main()