# Automated Instagram Account Creation System

A sophisticated Telegram bot with web dashboard for automated Instagram account creation, featuring email verification, profile setup, and 2FA configuration.

## 🏗️ Project Architecture

### 📱 Telegram Bot (Deployed on Render)
- **Purpose**: Core automation engine and user interface
- **Location**: `/bot/` directory
- **Deployment**: Render.com
- **Features**: Account creation, email verification, 2FA setup

### 🌐 Web Dashboard (Deployed on Netlify)
- **Purpose**: Real-time monitoring and management interface
- **Location**: `/webapp/` directory
- **Deployment**: Netlify.com
- **Features**: Live statistics, account management, bot control

## 📁 Directory Structure

```
instagram-automation/
├── bot/                          # Telegram Bot (Render)
│   ├── config.py
│   ├── automation_logic.py
│   ├── main_bot.py
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
├── webapp/                       # Web Dashboard (Netlify)
│   ├── index.html
│   ├── dashboard.js
│   ├── styles.css
│   └── netlify.toml
├── shared/                       # Shared Resources
│   ├── gmail_accounts.txt
│   ├── password.txt
│   ├── bot_state.json
│   └── credentials.json
└── docs/                         # Documentation
    ├── SETUP.md
    ├── DEPLOYMENT.md
    └── API.md
```

## 🚀 Quick Start

### 1. Bot Setup (Render)
1. Fork this repository
2. Configure environment variables in Render
3. Deploy bot service
4. Bot will be accessible via Telegram

### 2. Web Dashboard Setup (Netlify)
1. Connect GitHub repository to Netlify
2. Set build directory to `/webapp`
3. Deploy web dashboard
4. Access dashboard via Netlify URL

## 🔧 Configuration

### Bot Configuration
- Bot Token: Set in Render environment variables
- Gmail accounts: Upload to shared storage
- Google Sheets: Configure credentials

### Web Dashboard Configuration
- API endpoints: Configure to point to bot
- Real-time updates: WebSocket connection
- Authentication: Optional user management

## 📊 Features

### Telegram Bot Features
- ✅ Automated account creation
- ✅ Email verification handling
- ✅ Profile picture upload
- ✅ 2FA setup and key extraction
- ✅ Real-time status updates
- ✅ Error handling and recovery

### Web Dashboard Features
- 📈 Live statistics and progress
- 📋 Account management interface
- ⚙️ Bot configuration controls
- 📊 Success/failure analytics
- 🔄 Real-time monitoring

## 🔐 Security

- Environment variables for sensitive data
- Encrypted credential storage
- Secure API communication
- No hardcoded secrets

## 📞 Support

For issues and questions, please refer to the documentation in the `/docs` directory.
