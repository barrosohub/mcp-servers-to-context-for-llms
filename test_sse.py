# -*- coding: utf-8 -*-
import asyncio
import json
import requests
import time
from datetime import datetime

def test_health_endpoint():
    """Testa o endpoint de health check"""
    print("🧪 Testando endpoint de health...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"📊 Servidor: {data['server']} v{data['version']}")
        return True
    except Exception as e:
        print(f"❌ Health check falhou: {e}")
        return False

def test_sync_sse_endpoint(url: str, duration: int = 10):
    """Testa um endpoint SSE de forma síncrona"""
    print(f"🧪 Testando {url} por {duration} segundos...")
    
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
                    print(f"[{timestamp}] 📡 Evento #{event_count}: {message}")
                except json.JSONDecodeError:
                    print(f"📄 Raw data: {line}")
        
        print(f"🏁 Teste concluído. Total de eventos: {event_count}")
        return event_count > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_broadcast_api():
    """Testa o endpoint de broadcast"""
    print("🧪 Testando API de broadcast...")
    
    try:
        data = {
            "message": "Teste de broadcast do script de teste",
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
        print(f"✅ Broadcast enviado: {result['status']}")
        return True
    except Exception as e:
        print(f"❌ Erro no broadcast: {e}")
        return False

def test_all_endpoints():
    """Executa todos os testes em sequência"""
    print("🚀 Iniciando suite de testes FastAPI SSE")
    print("=" * 50)
    
    # Teste de health check
    if not test_health_endpoint():
        print("⚠️  Servidor não está respondendo. Executar: python main.py")
        return False
    
    print("\n" + "-" * 50)
    
    # Teste do stream principal
    stream_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/stream", 5)
    
    print("\n" + "-" * 50)
    
    # Teste do stream de métricas
    metrics_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/metrics", 5)
    
    print("\n" + "-" * 50)
    
    # Teste do canal personalizado
    channel_ok = test_sync_sse_endpoint("http://127.0.0.1:8000/realtime/test", 5)
    
    print("\n" + "-" * 50)
    
    # Teste da API de broadcast
    broadcast_ok = test_broadcast_api()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"   Health Check: {'✅' if True else '❌'}")
    print(f"   Stream Principal: {'✅' if stream_ok else '❌'}")
    print(f"   Métricas: {'✅' if metrics_ok else '❌'}")
    print(f"   Canal Personalizado: {'✅' if channel_ok else '❌'}")
    print(f"   Broadcast API: {'✅' if broadcast_ok else '❌'}")
    
    all_ok = stream_ok and metrics_ok and channel_ok and broadcast_ok
    print(f"\n🎯 Status Geral: {'✅ TODOS OS TESTES PASSARAM' if all_ok else '❌ ALGUNS TESTES FALHARAM'}")
    
    return all_ok

def interactive_test():
    """Teste interativo para escolher endpoints específicos"""
    print("🚀 FastAPI SSE - Teste Interativo")
    print("=" * 40)
    print("1. Health Check")
    print("2. Stream Principal (/stream)")
    print("3. Métricas (/metrics)")
    print("4. Canal Personalizado (/realtime/test)")
    print("5. API Broadcast")
    print("6. Executar Todos os Testes")
    print("7. Sair")
    print("=" * 40)
    
    while True:
        try:
            choice = input("\nEscolha uma opção (1-7): ").strip()
            
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
                print("👋 Encerrando testes...")
                break
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n🛑 Testes interrompidos pelo usuário")
            break
        except EOFError:
            print("\n👋 Encerrando testes...")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Modo automático
        test_all_endpoints()
    else:
        # Modo interativo
        interactive_test()
