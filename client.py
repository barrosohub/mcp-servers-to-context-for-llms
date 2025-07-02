# -*- coding: utf-8 -*-
import requests
import json
import time
import threading
import signal
import sys
from typing import Optional

class FastAPISSEClient:
    """Cliente Python para consumir Server-Sent Events do FastAPI"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.connections = {}
        self.running = False
        
    def connect(self, endpoint: str, callback=None):
        """Conecta a um endpoint SSE específico"""
        url = f"{self.base_url}{endpoint}"
        self.running = True
        
        try:
            print(f"🔗 Conectando a {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Conectado a {endpoint}")
            
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
                            continue  # Aguardar próxima linha com data
                        else:
                            continue
                            
                        if callback:
                            callback(event)
                        else:
                            self._default_handler(event, endpoint)
                            
                    except KeyboardInterrupt:
                        print("\n⚠️  Interrompido pelo usuário")
                        break
                    except Exception as e:
                        print(f"❌ Erro processando evento: {e}")
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        finally:
            self.running = False
            print(f"🔌 Desconectado de {endpoint}")
    
    def _default_handler(self, event, endpoint):
        """Handler padrão para eventos SSE"""
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
                message = data.get('message', 'Dados recebidos')
                print(f"[{timestamp}] 📝 {endpoint} - {message}")
                
        except json.JSONDecodeError:
            print(f"[{timestamp}] 📄 {endpoint} - Raw: {event['data']}")
    
    def stop(self):
        """Para todas as conexões"""
        self.running = False

def test_health():
    """Testa o endpoint de health"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check OK: {data['status']}")
        return True
    except Exception as e:
        print(f"❌ Health check falhou: {e}")
        return False

def main():
    """Demonstração do cliente"""
    print("🚀 FastAPI SSE Client")
    print("=" * 40)
    
    # Testar conexão primeiro
    if not test_health():
        print("⚠️  Servidor não está respondendo. Certifique-se de que está rodando:")
        print("   python main.py")
        return
    
    print("1. Stream Principal (/stream)")
    print("2. Métricas (/metrics)")
    print("3. Canal Personalizado (/realtime/demo)")
    print("4. Teste de Broadcast")
    print("5. Sair")
    print("=" * 40)
    
    client = FastAPISSEClient()
    
    while True:
        try:
            choice = input("\nEscolha uma opção (1-5): ").strip()
            
            if choice == '1':
                print("Conectando ao stream principal...")
                client.connect('/stream')
            elif choice == '2':
                print("Conectando às métricas...")
                client.connect('/metrics')
            elif choice == '3':
                print("Conectando ao canal demo...")
                client.connect('/realtime/demo')
            elif choice == '4':
                print("Enviando broadcast...")
                test_broadcast()
            elif choice == '5':
                print("👋 Encerrando...")
                break
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
            client.stop()
            break
        except EOFError:
            print("\n👋 Encerrando...")
            break

def test_broadcast():
    """Testa o endpoint de broadcast"""
    try:
        data = {
            "message": "Teste de broadcast do cliente Python",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post("http://127.0.0.1:8000/api/broadcast", json=data, timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Broadcast enviado: {result['status']}")
    except Exception as e:
        print(f"❌ Erro no broadcast: {e}")

if __name__ == "__main__":
    # Handler para sinais do sistema
    def signal_handler(sig, frame):
        print('\n🛑 Sinal recebido, encerrando...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    main() 