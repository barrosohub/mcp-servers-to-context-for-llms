# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import datetime
import random
from typing import AsyncGenerator
import uvicorn

app = FastAPI(
    title="FastAPI SSE Server", 
    version="1.0.0",
    description="Server-Sent Events com FastAPI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== TEMPLATE HTML COMPLETO ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI SSE Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: #333;
        }
        .controls { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .control-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #007bff;
        }
        button { 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600; 
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn-connect { background: #28a745; color: white; }
        .btn-disconnect { background: #dc3545; color: white; }
        .btn-clear { background: #6c757d; color: white; }
        button:hover { transform: translateY(-2px); opacity: 0.9; }
        .status { 
            padding: 15px; 
            border-radius: 6px; 
            font-weight: 600; 
            text-align: center; 
            margin: 10px 0;
        }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .events-container { 
            height: 400px; 
            overflow-y: auto; 
            background: #1a1a1a; 
            border-radius: 10px; 
            padding: 20px;
            font-family: 'Courier New', monospace;
        }
        .event { 
            background: #2d2d2d; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #007bff;
            color: #f8f9fa;
            font-size: 13px;
        }
        .event.heartbeat { border-left-color: #28a745; }
        .event.notification { border-left-color: #ffc107; }
        .event.sensor { border-left-color: #17a2b8; }
        .event.metrics { border-left-color: #fd7e14; }
        .event-header { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 8px; 
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FastAPI Server-Sent Events</h1>
            <p>Demonstração completa de SSE em tempo real</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalEvents">0</div>
                <div>Total</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="streamEvents">0</div>
                <div>Stream</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="metricsEvents">0</div>
                <div>Metrics</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <h4>📡 Main Stream</h4>
                <div class="status disconnected" id="streamStatus">Desconectado</div>
                <button class="btn-connect" onclick="connectStream()">Conectar</button>
                <button class="btn-disconnect" onclick="disconnectStream()">Desconectar</button>
            </div>
            
            <div class="control-group">
                <h4>📊 Metrics Stream</h4>
                <div class="status disconnected" id="metricsStatus">Desconectado</div>
                <button class="btn-connect" onclick="connectMetrics()">Conectar</button>
                <button class="btn-disconnect" onclick="disconnectMetrics()">Desconectar</button>
            </div>
            
            <div class="control-group">
                <h4>🎛️ Controles</h4>
                <button class="btn-connect" onclick="connectAll()">Conectar Todos</button>
                <button class="btn-disconnect" onclick="disconnectAll()">Desconectar Todos</button>
                <button class="btn-clear" onclick="clearEvents()">Limpar</button>
            </div>
        </div>
        
        <div class="events-container" id="eventsContainer">
            <div class="event">
                <div class="event-header">
                    <span>🚀 SISTEMA</span>
                    <span id="initialTime"></span>
                </div>
                <div>Cliente SSE iniciado. Conecte-se aos streams para ver eventos em tempo real.</div>
            </div>
        </div>
    </div>

    <script>
        // Inicializar timestamp
        document.getElementById('initialTime').textContent = new Date().toLocaleTimeString();
        
        let connections = { stream: null, metrics: null };
        let eventCounts = { total: 0, stream: 0, metrics: 0 };
        
        const eventsContainer = document.getElementById('eventsContainer');
        
        function updateStats() {
            document.getElementById('totalEvents').textContent = eventCounts.total;
            document.getElementById('streamEvents').textContent = eventCounts.stream;
            document.getElementById('metricsEvents').textContent = eventCounts.metrics;
        }
        
        function addEvent(source, type, data) {
            eventCounts.total++;
            eventCounts[source]++;
            updateStats();
            
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const icons = {
                stream: '📡', metrics: '📊', heartbeat: '💓', 
                notification: '🔔', sensor: '🌡️', error: '❌'
            };
            
            let displayData;
            try {
                const parsed = JSON.parse(data);
                if (parsed.metrics) {
                    displayData = `CPU: ${parsed.metrics.cpu_usage_percent}% | Memory: ${parsed.metrics.memory_usage_mb}MB | RPS: ${parsed.metrics.requests_per_second}`;
                } else if (parsed.sensor_data) {
                    displayData = `Temp: ${parsed.sensor_data.temperature}°C | Humidity: ${parsed.sensor_data.humidity}%`;
                } else {
                    displayData = parsed.message || JSON.stringify(parsed, null, 2);
                }
            } catch {
                displayData = data;
            }
            
            eventDiv.innerHTML = `
                <div class="event-header">
                    <span>${icons[type] || icons[source]} ${type.toUpperCase()}</span>
                    <span>${timestamp}</span>
                </div>
                <div>${displayData}</div>
            `;
            
            eventsContainer.insertBefore(eventDiv, eventsContainer.firstChild);
            
            if (eventsContainer.children.length > 50) {
                eventsContainer.removeChild(eventsContainer.lastChild);
            }
        }
        
        function updateStatus(source, status) {
            const statusElement = document.getElementById(`${source}Status`);
            statusElement.className = `status ${status}`;
            statusElement.textContent = status === 'connected' ? '🟢 Conectado' : '🔴 Desconectado';
        }
        
        function connect(source, endpoint) {
            if (connections[source]) {
                connections[source].close();
            }
            
            const eventSource = new EventSource(endpoint);
            connections[source] = eventSource;
            
            eventSource.onopen = () => updateStatus(source, 'connected');
            eventSource.onmessage = (event) => addEvent(source, source, event.data);
            eventSource.addEventListener('heartbeat', (event) => addEvent(source, 'heartbeat', event.data));
            eventSource.addEventListener('notification', (event) => addEvent(source, 'notification', event.data));
            eventSource.addEventListener('sensor', (event) => addEvent(source, 'sensor', event.data));
            eventSource.onerror = () => updateStatus(source, 'disconnected');
        }
        
        function disconnect(source) {
            if (connections[source]) {
                connections[source].close();
                connections[source] = null;
                updateStatus(source, 'disconnected');
            }
        }
        
        // Funções específicas
        function connectStream() { connect('stream', '/stream'); }
        function connectMetrics() { connect('metrics', '/metrics'); }
        function disconnectStream() { disconnect('stream'); }
        function disconnectMetrics() { disconnect('metrics'); }
        function connectAll() { connectStream(); connectMetrics(); }
        function disconnectAll() { disconnectStream(); disconnectMetrics(); }
        function clearEvents() { 
            eventsContainer.innerHTML = '<div class="event"><div class="event-header"><span>🧹 SISTEMA</span><span>' + new Date().toLocaleTimeString() + '</span></div><div>Eventos limpos.</div></div>'; 
            eventCounts = { total: 0, stream: 0, metrics: 0 };
            updateStats();
        }
        
        // Cleanup
        window.addEventListener('beforeunload', disconnectAll);
        updateStats();
    </script>
</body>
</html>
"""

# ==================== ENDPOINTS ====================

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Página principal com cliente SSE integrado"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/stream")
async def stream_events(request: Request):
    """
    Endpoint principal para Server-Sent Events
    Gera eventos diversos: mensagens, heartbeat, notificações, sensores
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        # Evento de conexão inicial
        initial_data = {
            'message': 'Conectado ao FastAPI SSE Server',
            'timestamp': datetime.datetime.now().isoformat(),
            'server_info': {
                'framework': 'FastAPI',
                'version': '1.0.0',
                'client_ip': str(request.client.host) if request.client else 'unknown'
            }
        }
        yield f"data: {json.dumps(initial_data)}\n\n"
        
        counter = 0
        while True:
            # Verificar se cliente ainda está conectado
            if await request.is_disconnected():
                break
                
            counter += 1
            
            try:
                # Evento de dados regulares (a cada 3 loops)
                if counter % 3 == 0:
                    data = {
                        'message': f'Atualização regular #{counter}',
                        'timestamp': datetime.datetime.now().isoformat(),
                        'random_value': random.randint(1, 100),
                        'status': 'active'
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Evento de heartbeat (a cada 5 loops)
                elif counter % 5 == 0:
                    heartbeat_data = {
                        'server_time': datetime.datetime.now().isoformat(),
                        'uptime_seconds': counter * 2,
                        'memory_usage': f"{random.randint(50, 90)}%",
                        'cpu_usage': f"{random.randint(10, 50)}%"
                    }
                    yield f"event: heartbeat\ndata: {json.dumps(heartbeat_data)}\n\n"
                
                # Evento de notificação (a cada 8 loops)
                elif counter % 8 == 0:
                    notifications = [
                        {'title': 'System Update', 'message': 'Nova versão disponível', 'level': 'info'},
                        {'title': 'Warning', 'message': 'Alto uso de memória detectado', 'level': 'warning'},
                        {'title': 'Success', 'message': 'Backup concluído com sucesso', 'level': 'success'},
                        {'title': 'Alert', 'message': 'Limite de conexões atingido', 'level': 'error'}
                    ]
                    notification = random.choice(notifications)
                    notification['timestamp'] = datetime.datetime.now().isoformat()
                    yield f"event: notification\ndata: {json.dumps(notification)}\n\n"
                
                # Dados de sensores simulados (a cada 4 loops)
                elif counter % 4 == 0:
                    sensor_data = {
                        'sensor_data': {
                            'temperature': round(random.uniform(18, 32), 2),
                            'humidity': round(random.uniform(30, 85), 2),
                            'pressure': round(random.uniform(995, 1025), 2),
                            'light': round(random.uniform(0, 100), 1)
                        },
                        'location': 'Server Room A',
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    yield f"event: sensor\ndata: {json.dumps(sensor_data)}\n\n"
                
                await asyncio.sleep(2)  # Intervalo entre eventos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                error_data = {
                    'error': str(e),
                    'timestamp': datetime.datetime.now().isoformat()
                }
                yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"  # Desabilitar buffering do nginx
        }
    )

@app.get("/metrics")
async def stream_metrics(request: Request):
    """
    Stream de métricas em tempo real
    Envia dados de performance do sistema a cada segundo
    """
    
    async def metrics_generator() -> AsyncGenerator[str, None]:
        # Evento inicial
        yield f"data: {json.dumps({'message': 'Conectado ao stream de métricas'})}\n\n"
        
        while True:
            if await request.is_disconnected():
                break
                
            metrics = {
                'timestamp': datetime.datetime.now().isoformat(),
                'metrics': {
                    'requests_per_second': random.randint(10, 100),
                    'response_time_ms': random.randint(50, 300),
                    'error_rate': round(random.uniform(0, 5), 2),
                    'active_connections': random.randint(5, 50),
                    'memory_usage_mb': random.randint(128, 512),
                    'cpu_usage_percent': random.randint(10, 80),
                    'disk_usage_percent': random.randint(20, 90),
                    'network_io_mbps': round(random.uniform(1, 100), 2)
                }
            }
            
            yield f"data: {json.dumps(metrics)}\n\n"
            await asyncio.sleep(1)  # Métricas a cada segundo
    
    return StreamingResponse(
        metrics_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/realtime/{channel}")
async def stream_channel(channel: str, request: Request):
    """
    Stream de canal específico
    Permite múltiplos canais de dados independentes
    """
    
    async def channel_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'message': f'Conectado ao canal: {channel}'})}\n\n"
        
        while True:
            if await request.is_disconnected():
                break
                
            data = {
                'channel': channel,
                'timestamp': datetime.datetime.now().isoformat(),
                'data': {
                    'value': random.randint(1, 1000),
                    'status': random.choice(['active', 'idle', 'processing']),
                    'users_online': random.randint(1, 25)
                }
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(3)
    
    return StreamingResponse(
        channel_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.post("/api/broadcast")
async def broadcast_message(message: dict):
    """
    API para enviar mensagem broadcast
    Em produção, usar Redis/RabbitMQ para pub/sub
    """
    broadcast_data = {
        'type': 'broadcast',
        'message': message.get('message', ''),
        'timestamp': datetime.datetime.now().isoformat(),
        'sender': 'API'
    }
    
    return {
        'status': 'Message queued for broadcast',
        'data': broadcast_data,
        'timestamp': datetime.datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'server': 'FastAPI SSE Server',
        'version': '1.0.0'
    }

if __name__ == "__main__":
    print("🚀 FastAPI SSE Server iniciando...")
    print("📱 Interface: http://127.0.0.1:8000")
    print("📡 Stream: http://127.0.0.1:8000/stream")
    print("📊 Metrics: http://127.0.0.1:8000/metrics")
    print("🔗 Channel: http://127.0.0.1:8000/realtime/{channel}")
    print("❤️  Health: http://127.0.0.1:8000/health")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 