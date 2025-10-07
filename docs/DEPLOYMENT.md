# 🚀 Deployment Guide

## 📋 Pre-Deployment Checklist

- [ ] Gmail accounts configured with app passwords
- [ ] Google Sheets API enabled and credentials ready
- [ ] Telegram bot token obtained
- [ ] All files properly configured
- [ ] GitHub repository created and pushed

## 🤖 Bot Deployment (Render)

### Step 1: Prepare Repository

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/instagram-automation.git
   git push -u origin main
   ```

2. **Verify File Structure**
   ```
   instagram-automation/
   ├── bot/
   │   ├── config.py
   │   ├── automation_logic.py
   │   ├── main_bot.py
   │   ├── requirements.txt
   │   ├── Procfile
   │   └── runtime.txt
   ├── webapp/
   ├── shared/
   └── docs/
   ```

### Step 2: Render Setup

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Authorize GitHub access

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Select your repository

3. **Configure Service**
   ```
   Name: instagram-automation-bot
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: bot
   Build Command: pip install -r requirements.txt
   Start Command: python main_bot.py
   ```

### Step 3: Environment Variables

Add these environment variables in Render dashboard:

```
BOT_TOKEN=8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o
DATABASE_URL=postgresql://instagram_bot_db_80km_user:klys5axBI9deyq12UQ6jYgUUrulpLzWY@dpg-d3iab0gdl3ps73d25up0-a/instagram_bot_db_80km
STATIC_PASSWORD=YourSecurePassword123!
SPREADSHEET_NAME=Instagram Accounts Database
WORKSHEET_NAME=Accounts
HEADLESS_MODE=True
DELAY_BETWEEN_ACCOUNTS=30
WEB_DASHBOARD_URL=https://your-netlify-app.netlify.app
LOG_LEVEL=INFO
LOG_FILE=/app/logs/bot.log
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

### Step 4: Initialize Database

Since we're using PostgreSQL instead of files, we need to initialize the database:

1. **Deploy the bot first** to create the database tables
2. **Add Gmail accounts** using the database initialization script
3. **Test the connection** to ensure everything works

**Database initialization commands:**
```bash
# Initialize database tables
python db_init.py init

# Add Gmail accounts from file
python db_init.py load /path/to/gmail_accounts.txt

# Check database status
python db_init.py status
```

### Step 5: Deploy Bot

1. **Deploy Service**
   - Click "Deploy" in Render dashboard
   - Wait for build to complete
   - Check logs for any errors

2. **Test Bot**
   - Send `/start` to your bot
   - Verify bot responds
   - Test `/status` command

## 🌐 Web Dashboard Deployment (Netlify)

### Step 1: Netlify Setup

1. **Create Netlify Account**
   - Go to [netlify.com](https://netlify.com)
   - Sign up with GitHub
   - Authorize GitHub access

2. **Create New Site**
   - Click "New site from Git"
   - Select GitHub
   - Choose your repository

### Step 2: Configure Build

```
Repository: yourusername/instagram-automation
Branch: main
Base directory: webapp
Build command: echo "Static site - no build required"
Publish directory: webapp
```

### Step 3: Environment Variables

Add these environment variables in Netlify:

```
BOT_API_URL=https://your-bot-render-url.onrender.com
```

### Step 4: Update Configuration

1. **Update netlify.toml**
   ```toml
   [build]
     publish = "webapp"
     command = "echo 'Static site - no build required'"

   [build.environment]
     NODE_VERSION = "18"

   [[redirects]]
     from = "/api/*"
     to = "https://your-bot-render-url.onrender.com/api/:splat"
     status = 200
   ```

2. **Update dashboard.js**
   ```javascript
   // Replace API endpoints with your Render URL
   const BOT_API_URL = 'https://your-bot-render-url.onrender.com';
   ```

### Step 5: Deploy Dashboard

1. **Deploy Site**
   - Click "Deploy site" in Netlify
   - Wait for deployment to complete
   - Get your site URL

2. **Test Dashboard**
   - Visit your Netlify URL
   - Verify dashboard loads
   - Test bot connection

## 🔗 Integration Setup

### Step 1: Add API Endpoints to Bot

Add this to `bot/main_bot.py`:

```python
from flask import Flask, jsonify, request
import threading

# Add Flask app for API
api_app = Flask(__name__)

@api_app.route('/api/bot/status')
def api_bot_status():
    state = load_bot_state()
    accounts = load_gmail_accounts()
    return jsonify({
        'status': 'online' if state['is_running'] else 'offline',
        'is_running': state['is_running'],
        'stats': {
            'total': len(accounts),
            'successful': state['successful'],
            'failed': state['failed'],
            'successRate': (state['successful'] / max(state['total_processed'], 1)) * 100
        }
    })

@api_app.route('/api/bot/start', methods=['POST'])
def api_start_bot():
    data = request.get_json()
    start_index = data.get('startIndex', 0)
    
    # Start automation logic here
    return jsonify({'success': True, 'message': 'Automation started'})

@api_app.route('/api/bot/stop', methods=['POST'])
def api_stop_bot():
    # Stop automation logic here
    return jsonify({'success': True, 'message': 'Automation stopped'})

@api_app.route('/api/accounts')
def api_get_accounts():
    # Return accounts data
    return jsonify([])

# Run API server in separate thread
def run_api_server():
    api_app.run(host='0.0.0.0', port=5000)

# Start API server
api_thread = threading.Thread(target=run_api_server)
api_thread.daemon = True
api_thread.start()
```

### Step 2: Update Web Dashboard

Update `webapp/dashboard.js`:

```javascript
// Replace mock API calls with real endpoints
const BOT_API_URL = 'https://your-bot-render-url.onrender.com';

async function fetchBotStatus() {
    try {
        const response = await fetch(`${BOT_API_URL}/api/bot/status`);
        if (response.ok) {
            const data = await response.json();
            this.botStatus = data.status;
            this.isRunning = data.is_running;
            this.stats = data.stats;
        }
    } catch (error) {
        console.error('Error fetching bot status:', error);
    }
}
```

## 🔧 Post-Deployment Configuration

### Step 1: Update URLs

1. **Update Bot Configuration**
   - Edit `bot/config.py`
   - Set `WEB_DASHBOARD_URL` to your Netlify URL

2. **Update Web Dashboard**
   - Edit `webapp/netlify.toml`
   - Update redirect URL to your Render URL

### Step 2: Test Integration

1. **Test Bot Commands**
   ```
   /start - Initialize bot
   /status - Check status
   /start_auto 0 - Start automation
   /stop - Stop automation
   ```

2. **Test Web Dashboard**
   - Visit Netlify URL
   - Check bot status
   - Test control buttons
   - Verify real-time updates

### Step 3: Monitor Deployment

1. **Render Monitoring**
   - Check service logs
   - Monitor resource usage
   - Set up alerts

2. **Netlify Monitoring**
   - Check deployment status
   - Monitor site performance
   - Review build logs

## 🛠️ Troubleshooting

### Common Issues

1. **Bot Not Starting**
   ```
   Error: Module not found
   Solution: Check requirements.txt and build logs
   
   Error: File not found
   Solution: Verify file paths and shared disk
   
   Error: Environment variable missing
   Solution: Check Render environment variables
   ```

2. **Web Dashboard Not Loading**
   ```
   Error: 404 on API calls
   Solution: Check API endpoints and CORS settings
   
   Error: Bot status not updating
   Solution: Verify bot API endpoints
   ```

3. **Integration Issues**
   ```
   Error: CORS errors
   Solution: Add CORS headers to Flask app
   
   Error: API timeout
   Solution: Check Render service status
   ```

### Debug Steps

1. **Check Logs**
   - Render: Service logs
   - Netlify: Build logs
   - Browser: Console errors

2. **Verify Configuration**
   - Environment variables
   - File paths
   - API endpoints

3. **Test Components**
   - Bot independently
   - Web dashboard independently
   - Integration together

## 📊 Monitoring & Maintenance

### 1. Health Checks

Add health check endpoints:

```python
@api_app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'bot_running': load_bot_state()['is_running']
    })
```

### 2. Logging

Set up proper logging:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('logs/bot.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### 3. Backup Strategy

- Regular backups of shared files
- Database backups (if using)
- Configuration backups

---

**Deployment Complete!** 🎉

Your Instagram automation system is now live with:
- ✅ Telegram bot running on Render
- ✅ Web dashboard running on Netlify
- ✅ Full integration between components
- ✅ Real-time monitoring and control

**Next Steps:**
1. Test all functionality
2. Monitor performance
3. Set up alerts
4. Plan maintenance schedule
