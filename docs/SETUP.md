# 🚀 Complete Setup Guide

## 📋 Prerequisites

### 1. Google Account Setup
- **2-Step Verification**: Enable on all Gmail accounts
- **App Passwords**: Generate for each account (Mail > Custom device)
- **Google Sheets API**: Enable and create service account

### 2. Telegram Bot Setup
- Create bot with [@BotFather](https://t.me/botfather)
- Get bot token: `8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o`

### 3. Required Software
- Python 3.11+
- Git
- WebDriver (Geckodriver for Firefox)

## 🏗️ Project Structure

```
instagram-automation/
├── bot/                    # Telegram Bot (Render)
│   ├── config.py          # Configuration
│   ├── automation_logic.py # Core automation
│   ├── main_bot.py        # Bot interface
│   ├── requirements.txt   # Dependencies
│   ├── Procfile          # Render config
│   └── runtime.txt       # Python version
├── webapp/                # Web Dashboard (Netlify)
│   ├── index.html        # Main page
│   ├── dashboard.js      # JavaScript logic
│   ├── styles.css       # Styling
│   └── netlify.toml     # Netlify config
├── shared/               # Shared Resources
│   ├── gmail_accounts.txt # Gmail accounts
│   ├── password.txt      # Static password
│   ├── bot_state.json    # Bot state
│   └── credentials_template.json # Google Sheets
└── docs/                 # Documentation
    ├── SETUP.md         # This file
    ├── DEPLOYMENT.md    # Deployment guide
    └── API.md          # API documentation
```

## ⚙️ Configuration Steps

### 1. Gmail Accounts Setup
Edit `shared/gmail_accounts.txt`:
```
your-email1@gmail.com,your-app-password-1
your-email2@gmail.com,your-app-password-2
your-email3@gmail.com,your-app-password-3
```

### 2. Static Password
Edit `shared/password.txt`:
```
YourSecurePassword123!
```

### 3. Google Sheets Setup
1. Create Google Sheet named "Instagram Accounts Database"
2. Create worksheet named "Accounts"
3. Add headers: Username, Email, Password, 2FA Key, Created At, Status
4. Download service account credentials as `shared/credentials.json`

### 4. Bot Configuration
Edit `bot/config.py` if needed:
```python
BOT_TOKEN = "8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o"
SPREADSHEET_NAME = "Instagram Accounts Database"
WORKSHEET_NAME = "Accounts"
```

## 🔧 Local Development

### 1. Bot Development
```bash
cd bot
pip install -r requirements.txt
python main_bot.py
```

### 2. Web Dashboard Development
```bash
cd webapp
# Serve with any static server
python -m http.server 8000
# Or use Live Server extension in VS Code
```

## 🚀 Deployment Guide

### Bot Deployment (Render)

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect GitHub account

2. **Deploy Bot Service**
   - Create new "Web Service"
   - Connect GitHub repository
   - Set build command: `pip install -r bot/requirements.txt`
   - Set start command: `cd bot && python main_bot.py`
   - Add environment variables:
     ```
     BOT_TOKEN=8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o
     SPREADSHEET_NAME=Instagram Accounts Database
     WORKSHEET_NAME=Accounts
     HEADLESS_MODE=True
     DELAY_BETWEEN_ACCOUNTS=30
     ```

3. **Upload Shared Files**
   - Upload `shared/` files to Render's persistent disk
   - Update file paths in `bot/config.py`

### Web Dashboard Deployment (Netlify)

1. **Create Netlify Account**
   - Sign up at [netlify.com](https://netlify.com)
   - Connect GitHub account

2. **Deploy Web Dashboard**
   - Create new site from Git
   - Select repository
   - Set build directory: `webapp`
   - Set publish directory: `webapp`
   - Deploy

3. **Configure API Endpoints**
   - Update `webapp/netlify.toml` with your Render bot URL
   - Update `webapp/dashboard.js` API endpoints

## 🔗 Integration

### Bot ↔ Web Dashboard Communication

1. **API Endpoints** (Add to bot):
   ```python
   # Add to main_bot.py
   from flask import Flask, jsonify
   
   app = Flask(__name__)
   
   @app.route('/api/bot/status')
   def bot_status():
       state = load_bot_state()
       return jsonify({
           'status': 'online' if state['is_running'] else 'offline',
           'is_running': state['is_running'],
           'stats': {
               'total': len(load_gmail_accounts()),
               'successful': state['successful'],
               'failed': state['failed'],
               'successRate': (state['successful'] / max(state['total_processed'], 1)) * 100
           }
       })
   ```

2. **Web Dashboard Updates**:
   - Real-time status updates
   - Live progress tracking
   - Account management interface

## 🛡️ Security Considerations

### 1. Environment Variables
- Never commit sensitive data
- Use Render's environment variables
- Rotate credentials regularly

### 2. File Security
- Secure shared files on Render
- Use encrypted storage for credentials
- Implement access controls

### 3. API Security
- Add authentication to API endpoints
- Use HTTPS for all communications
- Implement rate limiting

## 📊 Monitoring & Maintenance

### 1. Logs
- Monitor Render logs
- Set up log aggregation
- Track error patterns

### 2. Performance
- Monitor bot performance
- Track success rates
- Optimize delays

### 3. Updates
- Regular dependency updates
- Security patches
- Feature enhancements

## 🆘 Troubleshooting

### Common Issues

1. **Bot Not Starting**
   - Check environment variables
   - Verify file paths
   - Check logs for errors

2. **Web Dashboard Not Loading**
   - Verify Netlify deployment
   - Check API endpoint URLs
   - Clear browser cache

3. **Account Creation Fails**
   - Verify Gmail app passwords
   - Check Instagram rate limits
   - Monitor WebDriver issues

### Support Resources

- **Documentation**: `/docs/` directory
- **Logs**: Render dashboard
- **Issues**: GitHub issues page

## 📈 Advanced Features

### 1. Scaling
- Multiple bot instances
- Load balancing
- Database integration

### 2. Analytics
- Detailed reporting
- Performance metrics
- Success rate tracking

### 3. Automation
- Scheduled runs
- Auto-retry failed accounts
- Smart delay adjustment

---

**Ready to deploy?** Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide for step-by-step instructions!
