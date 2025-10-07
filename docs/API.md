# 📚 API Documentation

## 🔗 Base URLs

- **Bot API**: `https://your-bot-render-url.onrender.com`
- **Web Dashboard**: `https://your-netlify-app.netlify.app`

## 🤖 Bot API Endpoints

### Authentication
All API endpoints require proper CORS headers and are designed for internal use between the bot and web dashboard.

### 1. Bot Status
**GET** `/api/bot/status`

Get current bot status and statistics.

**Response:**
```json
{
  "status": "online|offline|processing",
  "is_running": true|false,
  "stats": {
    "total": 50,
    "successful": 45,
    "failed": 3,
    "successRate": 93.8
  }
}
```

**Example:**
```bash
curl https://your-bot-render-url.onrender.com/api/bot/status
```

### 2. Start Automation
**POST** `/api/bot/start`

Start the automation process from a specific index.

**Request Body:**
```json
{
  "startIndex": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Automation started",
  "startIndex": 0
}
```

**Example:**
```bash
curl -X POST https://your-bot-render-url.onrender.com/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{"startIndex": 0}'
```

### 3. Stop Automation
**POST** `/api/bot/stop`

Stop the currently running automation process.

**Response:**
```json
{
  "success": true,
  "message": "Automation stopped"
}
```

**Example:**
```bash
curl -X POST https://your-bot-render-url.onrender.com/api/bot/stop
```

### 4. Get Accounts
**GET** `/api/accounts`

Get list of all processed accounts.

**Query Parameters:**
- `status` (optional): Filter by status (`successful`, `failed`, `pending`)
- `limit` (optional): Limit number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "username": "insta_user_123",
    "email": "temp123@mailvn.site",
    "status": "successful",
    "createdAt": "2024-01-15 10:30:00",
    "secretKey": "JBSWY3DPEHPK3PXP"
  },
  {
    "id": 2,
    "username": "insta_user_456",
    "email": "temp456@mailvn.site",
    "status": "failed",
    "createdAt": "2024-01-15 10:35:00",
    "secretKey": null
  }
]
```

**Example:**
```bash
curl "https://your-bot-render-url.onrender.com/api/accounts?status=successful&limit=10"
```

### 5. Health Check
**GET** `/health`

Check if the bot service is healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1705312200.123,
  "bot_running": false,
  "uptime": 3600
}
```

## 🌐 Web Dashboard API

The web dashboard uses the bot API endpoints internally. No separate API is needed.

### Frontend Integration

**JavaScript Example:**
```javascript
class InstagramDashboard {
    async fetchBotStatus() {
        try {
            const response = await fetch(`${BOT_API_URL}/api/bot/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateUI(data);
            }
        } catch (error) {
            console.error('Error fetching bot status:', error);
        }
    }
    
    async startAutomation(startIndex = 0) {
        try {
            const response = await fetch(`${BOT_API_URL}/api/bot/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ startIndex })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showToast(data.message, 'success');
            }
        } catch (error) {
            this.showToast('Error starting automation: ' + error.message, 'error');
        }
    }
}
```

## 📊 Data Models

### Bot State
```json
{
  "is_running": false,
  "current_index": 0,
  "total_processed": 0,
  "successful": 0,
  "failed": 0,
  "last_updated": "2024-01-15 10:30:00",
  "started_at": "2024-01-15 10:00:00"
}
```

### Account Data
```json
{
  "id": 1,
  "username": "insta_user_123",
  "email": "temp123@mailvn.site",
  "password": "SecurePassword123!",
  "secretKey": "JBSWY3DPEHPK3PXP",
  "status": "successful|failed|pending",
  "createdAt": "2024-01-15 10:30:00",
  "processingTime": "2m 15s"
}
```

### Statistics
```json
{
  "total": 50,
  "successful": 45,
  "failed": 3,
  "pending": 2,
  "successRate": 93.8,
  "averageTime": "2m 30s",
  "totalTime": "2h 15m"
}
```

## 🔒 Security Considerations

### 1. CORS Configuration
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-netlify-app.netlify.app'])
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/bot/start')
@limiter.limit("5 per hour")
def start_bot():
    # Implementation
```

### 3. Authentication (Optional)
```python
from functools import wraps
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
```

## 📈 Error Handling

### Standard Error Response
```json
{
  "error": true,
  "message": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15 10:30:00"
}
```

### Common Error Codes
- `BOT_ALREADY_RUNNING`: Automation is already in progress
- `BOT_NOT_RUNNING`: No automation to stop
- `INVALID_START_INDEX`: Start index is out of range
- `ACCOUNTS_NOT_FOUND`: No Gmail accounts configured
- `GOOGLE_SHEETS_ERROR`: Error saving to Google Sheets
- `SELENIUM_ERROR`: WebDriver automation error
- `EMAIL_VERIFICATION_FAILED`: Gmail verification failed

### Error Handling Example
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': True,
        'message': 'Endpoint not found',
        'code': 'NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': True,
        'message': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500
```

## 🔄 WebSocket Integration (Advanced)

For real-time updates, consider WebSocket integration:

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to bot'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def broadcast_status_update():
    socketio.emit('status_update', {
        'is_running': bot_state['is_running'],
        'current_index': bot_state['current_index'],
        'stats': bot_state
    })
```

## 📝 Testing

### Unit Tests
```python
import unittest
from unittest.mock import patch, MagicMock

class TestBotAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_bot_status(self):
        response = self.app.get('/api/bot/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertIn('is_running', data)
    
    def test_start_automation(self):
        with patch('automation_logic.load_gmail_accounts') as mock_accounts:
            mock_accounts.return_value = [{'email': 'test@test.com', 'app_password': 'test'}]
            response = self.app.post('/api/bot/start', 
                                  json={'startIndex': 0})
            self.assertEqual(response.status_code, 200)
```

### Integration Tests
```bash
# Test bot API
curl -X GET https://your-bot-render-url.onrender.com/api/bot/status

# Test web dashboard
curl -X GET https://your-netlify-app.netlify.app/

# Test integration
curl -X POST https://your-bot-render-url.onrender.com/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{"startIndex": 0}'
```

## 🚀 Performance Optimization

### 1. Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=60)
def get_bot_status():
    return load_bot_state()
```

### 2. Database Integration
```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))
    status = Column(String(20))
    created_at = Column(DateTime)
```

### 3. Async Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_accounts_async(accounts):
    loop = asyncio.get_event_loop()
    tasks = []
    
    for account in accounts:
        task = loop.run_in_executor(executor, create_instagram_account, account)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

---

**API Documentation Complete!** 📚

This comprehensive API documentation covers all endpoints, data models, security considerations, and integration examples for your Instagram automation system.
