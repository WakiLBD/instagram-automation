# Telegram Bot Configuration
import os

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8377225782:AAE3jApxu-Tuadu8Sot85pN9QNt3JHytg3o')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://instagram_bot_db_80km_user:klys5axBI9deyq12UQ6jYgUUrulpLzWY@dpg-d3iab0gdl3ps73d25up0-a/instagram_bot_db_80km')

# Google Sheets Configuration
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Instagram Accounts Database')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Accounts')

# Automation Settings
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
DELAY_BETWEEN_ACCOUNTS = int(os.getenv('DELAY_BETWEEN_ACCOUNTS', '30'))
STATIC_PASSWORD = os.getenv('STATIC_PASSWORD', 'SecurePassword123!')

# Web Dashboard Configuration
WEB_DASHBOARD_URL = os.getenv('WEB_DASHBOARD_URL', 'https://your-netlify-app.netlify.app')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', '/app/logs/bot.log')

# Database Connection Settings
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))
DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
