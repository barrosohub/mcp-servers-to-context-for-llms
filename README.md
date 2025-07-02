# 🚀 FastAPI Server-Sent Events (SSE) Tutorial

This project demonstrates a complete implementation of **Server-Sent Events** using FastAPI, including a server, Python client, and web interface.

## 📋 Features

- ✅ **FastAPI Server** with multiple SSE endpoints
- ✅ **Modern and interactive Web Interface**
- ✅ **Python Client** for consuming streams
- ✅ **Multiple event types**: heartbeat, notifications, metrics, sensors
- ✅ **Support for custom channels**
- ✅ **Broadcast API**
- ✅ **Automated tests**

## ⚙️ Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python main.py
```

The server will start at `http://127.0.0.1:8000` with the following endpoints:

- 🏠 **Web Interface**: `http://127.0.0.1:8000/`
- 📡 **Main Stream**: `http://127.0.0.1:8000/stream`
- 📊 **Metrics**: `http://127.0.0.1:8000/metrics`
- 🔗 **Custom Channel**: `http://127.0.0.1:8000/realtime/{channel-name}`
- ❤️ **Health Check**: `http://127.0.0.1:8000/health`

## 🌐 Web Interface

Access `http://127.0.0.1:8000` to see the full web interface with:

- **Simultaneous connection** to multiple streams
- **Real-time statistics**
- **Modern and responsive interface**
- **Interactive controls** to connect/disconnect streams

## 🐍 Python Client

Run the Python client to test the endpoints:

```bash
python client.py
```

The client offers an interactive menu to:
1. Connect to the main stream
2. Connect to metrics
3. Connect to a custom channel
4. Test the broadcast API

## 🧪 Run Tests

### Automated Tests
```bash
python test_sse.py --auto
```

### Interactive Tests
```bash
python test_sse.py
```

The tests verify:
- ✅ Server health check
- ✅ Main event stream
- ✅ Metrics stream
- ✅ Custom channels
- ✅ Broadcast API

## 📊 Available Endpoints

### 🏠 GET `/`
Main web interface with an integrated SSE client.

### 📡 GET `/stream`
Main event stream with:
- Regular messages
- Heartbeat events
- System notifications
- Simulated sensor data

### 📊 GET `/metrics`
Real-time metrics stream:
- CPU and memory
- Requests per second
- Error rate
- Network I/O

### 🔗 GET `/realtime/{channel}`
Custom channel for specific streams.

### 💬 POST `/api/broadcast`
API to send broadcast messages:
```json
{
  "message": "Your message here",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### ❤️ GET `/health`
Server health check.

## 🛠️ Consuming with Tools

### 📮 Postman
1. Create a new GET request
2. URL: `http://127.0.0.1:8000/stream`
3. Headers:
   ```
   Accept: text/event-stream
   Cache-Control: no-cache
   ```

### 💻 VSCode (REST Client)
```http
### SSE Stream
GET http://127.0.0.1:8000/stream
Accept: text/event-stream

### Metrics
GET http://127.0.0.1:8000/metrics
Accept: text/event-stream
```

### 🔧 cURL
```bash
# Main stream
curl -N -H "Accept: text/event-stream" http://127.0.0.1:8000/stream

# Metrics
curl -N -H "Accept: text/event-stream" http://127.0.0.1:8000/metrics

# Health check
curl http://127.0.0.1:8000/health
```

## 📝 Project Structure

```
fastapi-sse-tutorial/
├── main.py           # Main FastAPI server
├── client.py         # Python client to consume SSE
├── test_sse.py       # Automated tests
├── requirements.txt  # Project dependencies
└── README.md         # Documentation
```

## 🔧 Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Requests**: HTTP client for tests

## 🎯 Use Cases

This project demonstrates how to implement:

- 📊 **Real-time dashboards**
- 🔔 **Push notifications**
- 📈 **System monitoring**
- 🌡️ **IoT sensor data**
- 💬 **Activity feeds**

## 🔄 Event Flow

1. Client connects to the SSE endpoint
2. Server sends an initial connection event
3. Server generates periodic events:
   - **Every 2s**: Regular messages or special events
   - **Every 4s**: Sensor data
   - **Every 5s**: Heartbeat
   - **Every 8s**: Notifications
4. Client processes events in real-time

## 🎨 Event Types

- **`message`**: Standard events with general data
- **`heartbeat`**: Server life signals
- **`notification`**: Alerts and notifications
- **`sensor`**: Simulated sensor data
- **`error`**: Error messages

## 🚦 Server Status

The server indicates its status through:
- ✅ **200 OK**: Server is running
- 🔄 **Connection keep-alive**: SSE connection is active
- 📡 **text/event-stream**: Correct Content-Type

## 📱 Compatibility

- ✅ **Modern browsers** (Chrome, Firefox, Safari, Edge)
- ✅ **Custom Python client**
- ✅ **API tools** (Postman, VSCode, cURL)
- ✅ **Mobile** (through the responsive web interface)

## 🔧 Troubleshooting

### Problem: Server doesn't start
```bash
# Check if port 8000 is busy
netstat -tulpn | grep :8000

# Try a different port
uvicorn main:app --host 127.0.0.1 --port 8080
```

### Problem: Events don't arrive
1. Check if the server is running: `curl http://127.0.0.1:8000/health`
2. Confirm SSE headers: `Accept: text/event-stream`
3. Disable cache: `Cache-Control: no-cache`

### Problem: CORS errors
The server is already configured with permissive CORS for development. In production, configure specific domains.

## 🎓 Next Steps

To expand this project:

1. 🔐 **Add JWT authentication**
2. 📊 **Integrate Prometheus metrics**
3. 🔄 **Set up Redis for distributed pub/sub**
4. 🐳 **Containerize with Docker**
5. ☁️ **Deploy to the cloud**

## 📚 Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

---

**Happy Coding! 🚀**