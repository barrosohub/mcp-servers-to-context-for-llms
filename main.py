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
    description="Server-Sent Events with FastAPI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== COMPLETE HTML TEMPLATE ====================

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
            <p>Complete real-time SSE demonstration</p>
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
                <div class="status disconnected" id="streamStatus">Disconnected</div>
                <button class="btn-connect" onclick="connectStream()">Connect</button>
                <button class="btn-disconnect" onclick="disconnectStream()">Disconnect</button>
            </div>
            
            <div class="control-group">
                <h4>📊 Metrics Stream</h4>
                <div class="status disconnected" id="metricsStatus">Disconnected</div>
                <button class="btn-connect" onclick="connectMetrics()">Connect</button>
                <button class="btn-disconnect" onclick="disconnectMetrics()">Disconnect</button>
            </div>
            
            <div class="control-group">
                <h4>🎛️ Controls</h4>
                <button class="btn-connect" onclick="connectAll()">Connect All</button>
                <button class="btn-disconnect" onclick="disconnectAll()">Disconnect All</button>
                <button class="btn-clear" onclick="clearEvents()">Clear</button>
            </div>
        </div>
        
        <div class="events-container" id="eventsContainer">
            <div class="event">
                <div class="event-header">
                    <span>🚀 SYSTEM</span>
                    <span id="initialTime"></span>
                </div>
                <div>SSE client initiated. Connect to streams to see real-time events.</div>
            </div>
        </div>
    </div>

    <script>
        // Initialize timestamp
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
            statusElement.textContent = status === 'connected' ? '🟢 Connected' : '🔴 Disconnected';
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
        
        // Specific functions
        function connectStream() { connect('stream', '/stream'); }
        function connectMetrics() { connect('metrics', '/metrics'); }
        function disconnectStream() { disconnect('stream'); }
        function disconnectMetrics() { disconnect('metrics'); }
        function connectAll() { connectStream(); connectMetrics(); }
        function disconnectAll() { disconnectStream(); disconnectMetrics(); }
        function clearEvents() { 
            eventsContainer.innerHTML = '<div class="event"><div class="event-header"><span>🧹 SYSTEM</span><span>' + new Date().toLocaleTimeString() + '</span></div><div>Events cleared.</div></div>'; 
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
    """Main page with integrated SSE client"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/stream")
async def stream_events(request: Request):
    """
    Main endpoint for Server-Sent Events
    Generates various events: messages, heartbeat, notifications, sensors
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        # Initial connection event
        initial_data = {
            'message': 'Connected to FastAPI SSE Server',
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
            # Check if the client is still connected
            if await request.is_disconnected():
                break
                
            counter += 1
            
            try:
                # Regular data event (every 3 loops)
                if counter % 3 == 0:
                    data = {
                        'message': f'Regular update #{counter}',
                        'timestamp': datetime.datetime.now().isoformat(),
                        'random_value': random.randint(1, 100),
                        'status': 'active'
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Heartbeat event (every 5 loops)
                elif counter % 5 == 0:
                    heartbeat_data = {
                        'server_time': datetime.datetime.now().isoformat(),
                        'uptime_seconds': counter * 2,
                        'memory_usage': f"{random.randint(50, 90)}%",
                        'cpu_usage': f"{random.randint(10, 50)}%"
                    }
                    yield f"event: heartbeat\ndata: {json.dumps(heartbeat_data)}\n\n"
                
                # Notification event (every 8 loops)
                elif counter % 8 == 0:
                    notifications = [
                        {'title': 'System Update', 'message': 'New version available', 'level': 'info'},
                        {'title': 'Warning', 'message': 'High memory usage detected', 'level': 'warning'},
                        {'title': 'Success', 'message': 'Backup completed successfully', 'level': 'success'},
                        {'title': 'Alert', 'message': 'Connection limit reached', 'level': 'error'}
                    ]
                    notification = random.choice(notifications)
                    notification['timestamp'] = datetime.datetime.now().isoformat()
                    yield f"event: notification\ndata: {json.dumps(notification)}\n\n"
                
                # Simulated sensor data (every 4 loops)
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
                
                await asyncio.sleep(2)  # Interval between events
                
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
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@app.get("/metrics")
async def stream_metrics(request: Request):
    """
    Real-time metrics stream
    Sends system performance data every second
    """
    
    async def metrics_generator() -> AsyncGenerator[str, None]:
        # Initial event
        yield f"data: {json.dumps({'message': 'Connected to the metrics stream'})}\n\n"
        
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
            await asyncio.sleep(1)  # Metrics every second
    
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
    Specific channel stream
    Allows multiple independent data channels
    """
    
    async def channel_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'message': f'Connected to channel: {channel}'})}\n\n"
        
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
    API to send a broadcast message
    In production, use Redis/RabbitMQ for pub/sub
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
    print("🚀 FastAPI SSE Server starting...")
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