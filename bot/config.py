# Telegram Bot Configuration
import os

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o')

# Google Sheets Configuration
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Instagram Accounts Database')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Accounts')

# Automation Settings
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
DELAY_BETWEEN_ACCOUNTS = int(os.getenv('DELAY_BETWEEN_ACCOUNTS', '30'))

# File Paths (for Render deployment)
GMAIL_ACCOUNTS_FILE = os.getenv('GMAIL_ACCOUNTS_FILE', '/app/shared/gmail_accounts.txt')
PASSWORD_FILE = os.getenv('PASSWORD_FILE', '/app/shared/password.txt')
BOT_STATE_FILE = os.getenv('BOT_STATE_FILE', '/app/shared/bot_state.json')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', '/app/shared/credentials.json')

# Web Dashboard Configuration
WEB_DASHBOARD_URL = os.getenv('WEB_DASHBOARD_URL', 'https://your-netlify-app.netlify.app')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', '/app/logs/bot.log')
