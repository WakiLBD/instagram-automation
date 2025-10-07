# Database Models and Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
import logging
from config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT

# Configure logging
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

class GmailAccount(Base):
    """Model for Gmail accounts used in automation"""
    __tablename__ = 'gmail_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    app_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<GmailAccount(email='{self.email}', active={self.is_active})>"

class InstagramAccount(Base):
    """Model for created Instagram accounts"""
    __tablename__ = 'instagram_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    temp_email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    secret_key = Column(String(255), nullable=True)
    status = Column(String(50), default='pending')  # pending, successful, failed
    processing_time = Column(Float, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InstagramAccount(username='{self.username}', status='{self.status}')>"

class BotState(Base):
    """Model for bot state management"""
    __tablename__ = 'bot_state'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_running = Column(Boolean, default=False)
    current_index = Column(Integer, default=0)
    total_processed = Column(Integer, default=0)
    successful_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotState(running={self.is_running}, index={self.current_index})>"

class AutomationLog(Base):
    """Model for automation activity logs"""
    __tablename__ = 'automation_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)  # info, warning, error
    message = Column(Text, nullable=False)
    account_id = Column(Integer, nullable=True)  # reference to InstagramAccount
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AutomationLog(level='{self.level}', message='{self.message[:50]}...')>"

# Database connection setup
class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database connection and create tables"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                pool_recycle=3600,  # Recycle connections every hour
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            session = self.get_session()
            # Use SQLAlchemy text() for textual SQL per SA 2.x requirements
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db_session():
    """Dependency to get database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

# Database utility functions
class DatabaseUtils:
    @staticmethod
    def add_gmail_account(email: str, app_password: str) -> bool:
        """Add a new Gmail account to the database"""
        try:
            session = db_manager.get_session()
            account = GmailAccount(email=email, app_password=app_password)
            session.add(account)
            session.commit()
            session.close()
            logger.info(f"Added Gmail account: {email}")
            return True
        except Exception as e:
            logger.error(f"Error adding Gmail account: {e}")
            return False
    
    @staticmethod
    def get_all_gmail_accounts() -> list:
        """Get all active Gmail accounts"""
        try:
            session = db_manager.get_session()
            accounts = session.query(GmailAccount).filter(GmailAccount.is_active == True).all()
            session.close()
            return accounts
        except Exception as e:
            logger.error(f"Error getting Gmail accounts: {e}")
            return []
    
    @staticmethod
    def get_unused_gmail_accounts() -> list:
        """Get all unused Gmail accounts"""
        try:
            session = db_manager.get_session()
            accounts = session.query(GmailAccount).filter(
                GmailAccount.is_active == True,
                GmailAccount.is_used == False
            ).all()
            session.close()
            return accounts
        except Exception as e:
            logger.error(f"Error getting unused Gmail accounts: {e}")
            return []
    
    @staticmethod
    def mark_gmail_account_used(email: str) -> bool:
        """Mark a Gmail account as used"""
        try:
            session = db_manager.get_session()
            account = session.query(GmailAccount).filter(GmailAccount.email == email).first()
            if account:
                account.is_used = True
                account.updated_at = datetime.utcnow()
                session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Error marking Gmail account as used: {e}")
            return False
    
    @staticmethod
    def add_instagram_account(username: str, email: str, temp_email: str, 
                           password: str, secret_key: str = None, 
                           status: str = 'successful', processing_time: float = None,
                           error_message: str = None) -> bool:
        """Add a new Instagram account to the database"""
        try:
            session = db_manager.get_session()
            account = InstagramAccount(
                username=username,
                email=email,
                temp_email=temp_email,
                password=password,
                secret_key=secret_key,
                status=status,
                processing_time=processing_time,
                error_message=error_message
            )
            session.add(account)
            session.commit()
            session.close()
            logger.info(f"Added Instagram account: {username}")
            return True
        except Exception as e:
            logger.error(f"Error adding Instagram account: {e}")
            return False
    
    @staticmethod
    def get_instagram_accounts(status: str = None) -> list:
        """Get Instagram accounts, optionally filtered by status"""
        try:
            session = db_manager.get_session()
            query = session.query(InstagramAccount)
            if status:
                query = query.filter(InstagramAccount.status == status)
            accounts = query.order_by(InstagramAccount.created_at.desc()).all()
            session.close()
            return accounts
        except Exception as e:
            logger.error(f"Error getting Instagram accounts: {e}")
            return []
    
    @staticmethod
    def get_bot_state() -> BotState:
        """Get current bot state"""
        try:
            session = db_manager.get_session()
            state = session.query(BotState).first()
            if not state:
                # Create initial state if none exists
                state = BotState()
                session.add(state)
                session.commit()
            session.close()
            return state
        except Exception as e:
            logger.error(f"Error getting bot state: {e}")
            return None
    
    @staticmethod
    def update_bot_state(is_running: bool = None, current_index: int = None,
                        total_processed: int = None, successful_count: int = None,
                        failed_count: int = None, started_at: datetime = None) -> bool:
        """Update bot state"""
        try:
            session = db_manager.get_session()
            state = session.query(BotState).first()
            if not state:
                state = BotState()
                session.add(state)
            
            if is_running is not None:
                state.is_running = is_running
            if current_index is not None:
                state.current_index = current_index
            if total_processed is not None:
                state.total_processed = total_processed
            if successful_count is not None:
                state.successful_count = successful_count
            if failed_count is not None:
                state.failed_count = failed_count
            if started_at is not None:
                state.started_at = started_at
            
            state.last_updated = datetime.utcnow()
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Error updating bot state: {e}")
            return False
    
    @staticmethod
    def add_automation_log(level: str, message: str, account_id: int = None) -> bool:
        """Add automation log entry"""
        try:
            session = db_manager.get_session()
            log = AutomationLog(level=level, message=message, account_id=account_id)
            session.add(log)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Error adding automation log: {e}")
            return False
    
    @staticmethod
    def get_recent_logs(limit: int = 50) -> list:
        """Get recent automation logs"""
        try:
            session = db_manager.get_session()
            logs = session.query(AutomationLog).order_by(
                AutomationLog.created_at.desc()
            ).limit(limit).all()
            session.close()
            return logs
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    @staticmethod
    def get_statistics() -> dict:
        """Get automation statistics"""
        try:
            session = db_manager.get_session()
            
            # Get counts
            total_accounts = session.query(InstagramAccount).count()
            successful_accounts = session.query(InstagramAccount).filter(
                InstagramAccount.status == 'successful'
            ).count()
            failed_accounts = session.query(InstagramAccount).filter(
                InstagramAccount.status == 'failed'
            ).count()
            pending_accounts = session.query(InstagramAccount).filter(
                InstagramAccount.status == 'pending'
            ).count()
            
            # Calculate success rate
            success_rate = 0
            if total_accounts > 0:
                success_rate = (successful_accounts / total_accounts) * 100
            
            # Get average processing time
            avg_time = session.query(InstagramAccount).filter(
                InstagramAccount.processing_time.isnot(None)
            ).with_entities(InstagramAccount.processing_time).all()
            
            avg_processing_time = 0
            if avg_time:
                times = [t[0] for t in avg_time if t[0] is not None]
                if times:
                    avg_processing_time = sum(times) / len(times)
            
            session.close()
            
            return {
                'total': total_accounts,
                'successful': successful_accounts,
                'failed': failed_accounts,
                'pending': pending_accounts,
                'success_rate': round(success_rate, 2),
                'avg_processing_time': round(avg_processing_time, 2)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'pending': 0,
                'success_rate': 0,
                'avg_processing_time': 0
            }

# Initialize database on import
try:
    if db_manager.test_connection():
        logger.info("Database initialized successfully")
    else:
        logger.error("Database initialization failed")
except Exception as e:
    logger.error(f"Database initialization error: {e}")
