import asyncio
import threading
import time
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import json
import os
from config import *
from automation_logic import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.automation_thread = None
        self.is_running = False
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Automated Instagram Account Creator Bot**

**Available Commands:**
/start - Initialize the bot
/start_auto <index> - Start automation from specific index
/stop - Stop current automation process
/status - Check current bot status
/help - Show this help message

**Ready to begin account creation automation!**
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 **Bot Commands Guide**

**Basic Commands:**
• `/start` - Initialize the bot
• `/help` - Show this help message

**Automation Commands:**
• `/start_auto <index>` - Start automation from specific account index
• `/stop` - Stop current automation process
• `/status` - Check current bot status

**Examples:**
• `/start_auto 0` - Start from first account
• `/start_auto 5` - Start from 6th account
• `/status` - Check current progress

**Note:** The bot will process accounts sequentially and save all data to Google Sheets.
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def start_auto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start_auto command"""
        try:
            # Check if automation is already running
            state = load_bot_state()
            if state['is_running']:
                await update.message.reply_text(
                    "⚠️ Automation is already running! Use `/stop` to stop it first.",
                    parse_mode='Markdown'
                )
                return
            
            # Get starting index
            if context.args and context.args[0].isdigit():
                start_index = int(context.args[0])
            else:
                start_index = 0
            
            # Load accounts and validate
            accounts = load_gmail_accounts()
            if not accounts:
                await update.message.reply_text(
                    "❌ No Gmail accounts found! Please check your configuration.",
                    parse_mode='Markdown'
                )
                return
            
            if start_index >= len(accounts):
                await update.message.reply_text(
                    f"❌ Starting index {start_index} is out of range. Total accounts: {len(accounts)}",
                    parse_mode='Markdown'
                )
                return
            
            # Start automation
            self.is_running = True
            self.automation_thread = threading.Thread(
                target=self.run_automation,
                args=(start_index, update.message.chat_id)
            )
            self.automation_thread.daemon = True
            self.automation_thread.start()
            
            # Send confirmation
            confirmation_message = f"""
🚀 **Automation Started!**

📊 **Configuration Loaded:**
• Starting from index: {start_index}
• Total accounts in queue: {len(accounts)}
• Static password: **********
• Headless mode: {HEADLESS_MODE}

⏳ **Beginning account creation process...**
            """
            await update.message.reply_text(confirmation_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error starting automation: {e}")
            await update.message.reply_text(
                f"❌ Error starting automation: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        try:
            state = load_bot_state()
            if not state['is_running']:
                await update.message.reply_text(
                    "ℹ️ No automation is currently running.",
                    parse_mode='Markdown'
                )
                return
            
            # Stop automation
            state['is_running'] = False
            save_bot_state(state)
            self.is_running = False
            
            # Send stop confirmation
            stop_message = f"""
🛑 **Automation Stopped!**

📊 **Session Summary:**
• Duration: {self.get_session_duration()}
• Accounts processed: {state['total_processed']}
• Successfully created: {state['successful']}
• Failed: {state['failed']}
• Last processed index: {state['current_index']}

💾 **State saved. Use `/start_auto {state['current_index']}` to resume.**
            """
            await update.message.reply_text(stop_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error stopping automation: {e}")
            await update.message.reply_text(
                f"❌ Error stopping automation: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            state = load_bot_state()
            accounts = load_gmail_accounts()
            
            if state['is_running']:
                status_icon = "🔄"
                status_text = "RUNNING"
            else:
                status_icon = "⏸️"
                status_text = "STOPPED"
            
            success_rate = 0
            if state['total_processed'] > 0:
                success_rate = (state['successful'] / state['total_processed']) * 100
            
            status_message = f"""
📊 **Current Automation Status**

{status_icon} **Process:** {status_text}
📅 **Started:** {state.get('started_at', 'N/A')}
✅ **Completed:** {state['successful']} accounts
❌ **Failed:** {state['failed']} accounts
⏳ **Current:** Processing account #{state['current_index'] + 1}
⏰ **ETA:** {self.calculate_eta(state, accounts)}

📈 **Success Rate:** {success_rate:.1f}%
📋 **Total Accounts:** {len(accounts)}
            """
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text(
                f"❌ Error getting status: {str(e)}",
                parse_mode='Markdown'
            )
    
    def run_automation(self, start_index, chat_id):
        """Main automation loop"""
        try:
            # Load data
            accounts = load_gmail_accounts()
            static_password = load_static_password()
            
            # Update state
            state = load_bot_state()
            state['is_running'] = True
            state['current_index'] = start_index
            state['started_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            save_bot_state(state)
            
            # Process accounts
            for i in range(start_index, len(accounts)):
                if not state['is_running']:
                    break
                
                account = accounts[i]
                logger.info(f"Processing account {i+1}/{len(accounts)}: {account['email']}")
                
                # Send progress update
                asyncio.run(self.send_progress_update(chat_id, i+1, len(accounts), account['email']))
                
                # Create Instagram account
                account_data = create_instagram_account(
                    account['email'],
                    account['app_password'],
                    static_password
                )
                
                if account_data:
                    # Save to Google Sheets
                    save_to_google_sheets(account_data)
                    
                    # Update state
                    state['successful'] += 1
                    state['total_processed'] += 1
                    
                    # Send success message
                    asyncio.run(self.send_success_message(chat_id, i+1, account_data))
                else:
                    # Update state
                    state['failed'] += 1
                    state['total_processed'] += 1
                    
                    # Send failure message
                    asyncio.run(self.send_failure_message(chat_id, i+1, account['email']))
                
                # Update current index
                state['current_index'] = i + 1
                save_bot_state(state)
                
                # Delay between accounts
                if i < len(accounts) - 1:
                    time.sleep(DELAY_BETWEEN_ACCOUNTS)
            
            # Send completion message
            if state['is_running']:
                asyncio.run(self.send_completion_message(chat_id, state))
            
            # Update final state
            state['is_running'] = False
            save_bot_state(state)
            
        except Exception as e:
            logger.error(f"Error in automation loop: {e}")
            asyncio.run(self.send_error_message(chat_id, str(e)))
    
    async def send_progress_update(self, chat_id, current, total, email):
        """Send progress update message"""
        try:
            message = f"""
🔄 **Processing Account #{current} ({current}/{total})**
📧 **Gmail:** {email}
⏰ **Started:** {time.strftime('%H:%M:%S')}
            """
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except TelegramError as e:
            logger.error(f"Error sending progress update: {e}")
    
    async def send_success_message(self, chat_id, account_num, account_data):
        """Send success message"""
        try:
            message = f"""
✅ **Account #{account_num} Created Successfully!**

📋 **Account Details:**
• Username: {account_data['username']}
• Temp Email: {account_data['temp_email']}
• Password: **********
• 2FA Key: {account_data['secret_key']}
• Status: Active

💾 **Saved to Google Sheets**
⏱️ **Processing time:** {account_data.get('processing_time', 'N/A')}
            """
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except TelegramError as e:
            logger.error(f"Error sending success message: {e}")
    
    async def send_failure_message(self, chat_id, account_num, email):
        """Send failure message"""
        try:
            message = f"""
❌ **Account #{account_num} Failed!**

⚠️ **Error Details:**
• Gmail: {email}
• Error: Account creation failed
• Action: Skipping to next account

📊 **Current Stats:**
• Successful: {load_bot_state()['successful']}
• Failed: {load_bot_state()['failed']}
• Remaining: {len(load_gmail_accounts()) - account_num}
            """
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except TelegramError as e:
            logger.error(f"Error sending failure message: {e}")
    
    async def send_completion_message(self, chat_id, state):
        """Send completion message"""
        try:
            success_rate = 0
            if state['total_processed'] > 0:
                success_rate = (state['successful'] / state['total_processed']) * 100
            
            message = f"""
🎉 **Automation Complete!**

📊 **Final Report:**
• Total accounts processed: {state['total_processed']}
• Successfully created: {state['successful']} ({success_rate:.1f}%)
• Failed: {state['failed']}
• Total duration: {self.get_session_duration()}

📁 **Data saved to Google Sheets:**
• Usernames, emails, passwords, 2FA keys
• Ready for distribution or further processing

🔄 **Use `/start_auto` to begin new session.**
            """
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except TelegramError as e:
            logger.error(f"Error sending completion message: {e}")
    
    async def send_error_message(self, chat_id, error):
        """Send error message"""
        try:
            message = f"""
❌ **Automation Error!**

⚠️ **Error Details:**
{error}

🛑 **Automation stopped. Check logs for more details.**
            """
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        except TelegramError as e:
            logger.error(f"Error sending error message: {e}")
    
    def get_session_duration(self):
        """Calculate session duration"""
        state = load_bot_state()
        if 'started_at' in state:
            start_time = time.strptime(state['started_at'], '%Y-%m-%d %H:%M:%S')
            current_time = time.localtime()
            duration = time.mktime(current_time) - time.mktime(start_time)
            return f"{int(duration // 3600)}h {int((duration % 3600) // 60)}m"
        return "N/A"
    
    def calculate_eta(self, state, accounts):
        """Calculate estimated time to completion"""
        if not state['is_running'] or state['current_index'] >= len(accounts):
            return "N/A"
        
        remaining = len(accounts) - state['current_index']
        avg_time_per_account = 5  # minutes
        eta_minutes = remaining * avg_time_per_account
        
        if eta_minutes < 60:
            return f"{eta_minutes}m"
        else:
            hours = eta_minutes // 60
            minutes = eta_minutes % 60
            return f"{hours}h {minutes}m"
    
    def setup_handlers(self):
        """Setup command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("start_auto", self.start_auto_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    def run(self):
        """Run the bot"""
        try:
            self.setup_handlers()
            logger.info("Starting Instagram automation bot...")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()
