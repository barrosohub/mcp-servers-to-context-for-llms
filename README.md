# 🚀 FastAPI Server-Sent Events (SSE) Tutorial

Este projeto demonstra uma implementação completa de **Server-Sent Events** usando FastAPI, incluindo servidor, cliente Python e interface web.

## 📋 Funcionalidades

- ✅ **Servidor FastAPI** com múltiplos endpoints SSE
- ✅ **Interface Web** moderna e interativa
- ✅ **Cliente Python** para consumo de streams
- ✅ **Múltiplos tipos de eventos**: heartbeat, notificações, métricas, sensores
- ✅ **Suporte a canais personalizados**
- ✅ **API de Broadcast**
- ✅ **Testes automatizados**

## ⚙️ Configuração do Ambiente

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Servidor

```bash
python main.py
```

O servidor iniciará em `http://127.0.0.1:8000` com os seguintes endpoints:

- 🏠 **Interface Web**: `http://127.0.0.1:8000/`
- 📡 **Stream Principal**: `http://127.0.0.1:8000/stream`
- 📊 **Métricas**: `http://127.0.0.1:8000/metrics`
- 🔗 **Canal Personalizado**: `http://127.0.0.1:8000/realtime/{nome-do-canal}`
- ❤️ **Health Check**: `http://127.0.0.1:8000/health`

## 🌐 Interface Web

Acesse `http://127.0.0.1:8000` para ver a interface web completa com:

- **Conexão simultânea** a múltiplos streams
- **Estatísticas em tempo real**
- **Interface moderna** e responsiva
- **Controles interativos** para conectar/desconectar streams

## 🐍 Cliente Python

Execute o cliente Python para testar os endpoints:

```bash
python client.py
```

O cliente oferece um menu interativo para:
1. Conectar ao stream principal
2. Conectar às métricas
3. Conectar a canal personalizado
4. Testar API de broadcast

## 🧪 Executar Testes

### Testes Automáticos
```bash
python test_sse.py --auto
```

### Testes Interativos
```bash
python test_sse.py
```

Os testes verificam:
- ✅ Health check do servidor
- ✅ Stream principal de eventos
- ✅ Stream de métricas
- ✅ Canais personalizados
- ✅ API de broadcast

## 📊 Endpoints Disponíveis

### 🏠 GET `/`
Interface web principal com cliente SSE integrado

### 📡 GET `/stream`
Stream principal de eventos com:
- Mensagens regulares
- Eventos de heartbeat
- Notificações do sistema
- Dados de sensores simulados

### 📊 GET `/metrics`
Stream de métricas em tempo real:
- CPU e memória
- Requisições por segundo
- Taxa de erro
- I/O de rede

### 🔗 GET `/realtime/{channel}`
Canal personalizado para streams específicos

### 💬 POST `/api/broadcast`
API para enviar mensagens broadcast:
```json
{
  "message": "Sua mensagem aqui",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### ❤️ GET `/health`
Health check do servidor

## 🛠️ Consumindo via Ferramentas

### 📮 Postman
1. Criar nova requisição GET
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

### Métricas
GET http://127.0.0.1:8000/metrics
Accept: text/event-stream
```

### 🔧 cURL
```bash
# Stream principal
curl -N -H "Accept: text/event-stream" http://127.0.0.1:8000/stream

# Métricas
curl -N -H "Accept: text/event-stream" http://127.0.0.1:8000/metrics

# Health check
curl http://127.0.0.1:8000/health
```

## 📝 Estrutura do Projeto

```
fastapi-sse-tutorial/
├── main.py           # Servidor FastAPI principal
├── client.py         # Cliente Python para consumir SSE
├── test_sse.py       # Testes automatizados
├── requirements.txt  # Dependências do projeto
└── README.md         # Documentação
```

## 🔧 Dependências

- **FastAPI**: Framework web moderno
- **Uvicorn**: Servidor ASGI
- **Requests**: Cliente HTTP para testes

## 🎯 Casos de Uso

Este projeto demonstra como implementar:

- 📊 **Dashboards em tempo real**
- 🔔 **Notificações push**
- 📈 **Monitoramento de sistemas**
- 🌡️ **Dados de sensores IoT**
- 💬 **Feeds de atividade**

## 🔄 Fluxo de Eventos

1. Cliente se conecta ao endpoint SSE
2. Servidor envia evento inicial de conexão
3. Servidor gera eventos periódicos:
   - **A cada 2s**: Mensagens regulares ou eventos especiais
   - **A cada 4s**: Dados de sensores
   - **A cada 5s**: Heartbeat
   - **A cada 8s**: Notificações
4. Cliente processa eventos em tempo real

## 🎨 Tipos de Eventos

- **`message`**: Eventos padrão com dados gerais
- **`heartbeat`**: Sinais de vida do servidor
- **`notification`**: Alertas e notificações
- **`sensor`**: Dados simulados de sensores
- **`error`**: Mensagens de erro

## 🚦 Status do Servidor

O servidor indica seu status através de:
- ✅ **200 OK**: Servidor funcionando
- 🔄 **Connection keep-alive**: Conexão SSE ativa
- 📡 **text/event-stream**: Content-Type correto

## 📱 Compatibilidade

- ✅ **Navegadores modernos** (Chrome, Firefox, Safari, Edge)
- ✅ **Cliente Python** personalizado
- ✅ **Ferramentas de API** (Postman, VSCode, cURL)
- ✅ **Mobile** (através da interface web responsiva)

## 🔧 Troubleshooting

### Problema: Servidor não inicia
```bash
# Verificar se a porta 8000 está ocupada
netstat -tulpn | grep :8000

# Tentar porta diferente
uvicorn main:app --host 127.0.0.1 --port 8080
```

### Problema: Eventos não chegam
1. Verificar se o servidor está executando: `curl http://127.0.0.1:8000/health`
2. Confirmar headers SSE: `Accept: text/event-stream`
3. Desabilitar cache: `Cache-Control: no-cache`

### Problema: CORS errors
O servidor já está configurado com CORS permissivo para desenvolvimento. Em produção, configure domínios específicos.

## 🎓 Próximos Passos

Para expandir este projeto:

1. 🔐 **Adicionar autenticação JWT**
2. 📊 **Integrar métricas do Prometheus**
3. 🔄 **Configurar Redis para pub/sub distribuído**
4. 🐳 **Containerizar com Docker**
5. ☁️ **Deploy em cloud**

## 📚 Recursos Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

---

**Happy Coding! 🚀**

