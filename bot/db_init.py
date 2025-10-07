# Database Initialization Script
import logging
from database import db_manager, DatabaseUtils, GmailAccount
from config import STATIC_PASSWORD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with sample data"""
    try:
        logger.info("Starting database initialization...")
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection failed!")
            return False
        
        logger.info("Database connection successful!")
        
        # Check if Gmail accounts already exist
        existing_accounts = DatabaseUtils.get_all_gmail_accounts()
        if existing_accounts:
            logger.info(f"Found {len(existing_accounts)} existing Gmail accounts")
            return True
        
        # Add sample Gmail accounts (replace with your actual accounts)
        sample_accounts = [
            ("account1@gmail.com", "abcd efgh ijkl mnop"),
            ("account2@gmail.com", "pqrs tuvw xyzq 1234"),
            ("account3@gmail.com", "5678 9abc defg hijk"),
            ("account4@gmail.com", "lmnop qrst uvwx yzab"),
            ("account5@gmail.com", "cdef ghij klmn opqr"),
        ]
        
        logger.info("Adding sample Gmail accounts...")
        for email, app_password in sample_accounts:
            success = DatabaseUtils.add_gmail_account(email, app_password)
            if success:
                logger.info(f"Added Gmail account: {email}")
            else:
                logger.error(f"Failed to add Gmail account: {email}")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def add_gmail_accounts_from_file(file_path: str):
    """Add Gmail accounts from a text file"""
    try:
        logger.info(f"Loading Gmail accounts from file: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        added_count = 0
        for line in lines:
            line = line.strip()
            if line and ',' in line:
                email, app_password = line.split(',', 1)
                email = email.strip()
                app_password = app_password.strip()
                
                success = DatabaseUtils.add_gmail_account(email, app_password)
                if success:
                    added_count += 1
                    logger.info(f"Added Gmail account: {email}")
                else:
                    logger.error(f"Failed to add Gmail account: {email}")
        
        logger.info(f"Successfully added {added_count} Gmail accounts")
        return True
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error loading Gmail accounts from file: {e}")
        return False

def reset_database():
    """Reset database (WARNING: This will delete all data!)"""
    try:
        logger.warning("Resetting database - ALL DATA WILL BE LOST!")
        
        # Drop all tables
        from database import Base
        Base.metadata.drop_all(bind=db_manager.engine)
        
        # Recreate tables
        Base.metadata.create_all(bind=db_manager.engine)
        
        logger.info("Database reset completed")
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False

def show_database_status():
    """Show current database status"""
    try:
        logger.info("Database Status:")
        
        # Test connection
        if db_manager.test_connection():
            logger.info("✓ Database connection: OK")
        else:
            logger.error("✗ Database connection: FAILED")
            return
        
        # Get statistics
        stats = DatabaseUtils.get_statistics()
        logger.info(f"✓ Total Instagram accounts: {stats['total']}")
        logger.info(f"✓ Successful accounts: {stats['successful']}")
        logger.info(f"✓ Failed accounts: {stats['failed']}")
        logger.info(f"✓ Pending accounts: {stats['pending']}")
        logger.info(f"✓ Success rate: {stats['success_rate']}%")
        logger.info(f"✓ Average processing time: {stats['avg_processing_time']}s")
        
        # Get Gmail accounts
        gmail_accounts = DatabaseUtils.get_all_gmail_accounts()
        logger.info(f"✓ Gmail accounts: {len(gmail_accounts)}")
        
        # Get bot state
        bot_state = DatabaseUtils.get_bot_state()
        if bot_state:
            logger.info(f"✓ Bot running: {bot_state.is_running}")
            logger.info(f"✓ Current index: {bot_state.current_index}")
            logger.info(f"✓ Total processed: {bot_state.total_processed}")
        
        # Get recent logs
        recent_logs = DatabaseUtils.get_recent_logs(5)
        logger.info(f"✓ Recent logs: {len(recent_logs)} entries")
        
    except Exception as e:
        logger.error(f"Error showing database status: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            initialize_database()
        elif command == "load":
            if len(sys.argv) > 2:
                file_path = sys.argv[2]
                add_gmail_accounts_from_file(file_path)
            else:
                logger.error("Please provide file path: python db_init.py load /path/to/gmail_accounts.txt")
        elif command == "reset":
            reset_database()
        elif command == "status":
            show_database_status()
        else:
            logger.error("Unknown command. Available commands: init, load, reset, status")
    else:
        # Default: initialize database
        initialize_database()
