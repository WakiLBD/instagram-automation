# 🗄️ Database Migration Guide

## 📋 Overview

This guide explains how to migrate from file-based storage to PostgreSQL database for the Instagram automation system.

## 🔄 Migration Benefits

### Before (File-based)
- ❌ Data lost on bot restart/redeploy
- ❌ No persistent state management
- ❌ Limited scalability
- ❌ No data relationships
- ❌ Manual file management

### After (Database-based)
- ✅ Persistent data across restarts
- ✅ Relational data management
- ✅ Scalable architecture
- ✅ ACID compliance
- ✅ Advanced querying capabilities
- ✅ Data integrity and consistency

## 🏗️ Database Schema

### Tables Created

#### 1. `gmail_accounts`
```sql
CREATE TABLE gmail_accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    app_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `instagram_accounts`
```sql
CREATE TABLE instagram_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    temp_email VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    secret_key VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    processing_time FLOAT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `bot_state`
```sql
CREATE TABLE bot_state (
    id SERIAL PRIMARY KEY,
    is_running BOOLEAN DEFAULT FALSE,
    current_index INTEGER DEFAULT 0,
    total_processed INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. `automation_logs`
```sql
CREATE TABLE automation_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    account_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Migration Steps

### Step 1: Database Setup

1. **Create PostgreSQL Database on Render**
   - Go to Render dashboard
   - Create new PostgreSQL database
   - Note the connection URL

2. **Update Environment Variables**
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

### Step 2: Code Migration

1. **Install Database Dependencies**
   ```bash
   pip install sqlalchemy psycopg2-binary
   ```

2. **Update Configuration**
   - Remove file path configurations
   - Add database URL configuration
   - Update environment variables

3. **Replace File Operations**
   - Replace `load_gmail_accounts()` with database queries
   - Replace `load_bot_state()` with database queries
   - Replace `save_bot_state()` with database updates

### Step 3: Data Migration

1. **Initialize Database Tables**
   ```bash
   python db_init.py init
   ```

2. **Migrate Gmail Accounts**
   ```bash
   # From existing file
   python db_init.py load gmail_accounts.txt
   
   # Or manually add accounts
   python -c "
   from database import DatabaseUtils
   DatabaseUtils.add_gmail_account('email@gmail.com', 'app_password')
   "
   ```

3. **Verify Migration**
   ```bash
   python db_init.py status
   ```

## 🔧 Database Operations

### Adding Gmail Accounts

```python
from database import DatabaseUtils

# Add single account
DatabaseUtils.add_gmail_account('email@gmail.com', 'app_password')

# Add multiple accounts
accounts = [
    ('email1@gmail.com', 'password1'),
    ('email2@gmail.com', 'password2'),
]
for email, password in accounts:
    DatabaseUtils.add_gmail_account(email, password)
```

### Managing Bot State

```python
from database import DatabaseUtils

# Get current state
state = DatabaseUtils.get_bot_state()

# Update state
DatabaseUtils.update_bot_state(
    is_running=True,
    current_index=5,
    successful_count=10
)
```

### Querying Instagram Accounts

```python
from database import DatabaseUtils

# Get all accounts
accounts = DatabaseUtils.get_instagram_accounts()

# Get successful accounts only
successful = DatabaseUtils.get_instagram_accounts('successful')

# Get statistics
stats = DatabaseUtils.get_statistics()
```

## 📊 Database Monitoring

### Health Checks

```python
from database import db_manager

# Test connection
if db_manager.test_connection():
    print("Database connected successfully")
else:
    print("Database connection failed")
```

### Performance Monitoring

```python
# Get database statistics
stats = DatabaseUtils.get_statistics()
print(f"Total accounts: {stats['total']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average processing time: {stats['avg_processing_time']}s")
```

## 🛠️ Database Maintenance

### Regular Tasks

1. **Backup Database**
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

2. **Clean Old Logs**
   ```sql
   DELETE FROM automation_logs 
   WHERE created_at < NOW() - INTERVAL '30 days';
   ```

3. **Optimize Performance**
   ```sql
   -- Create indexes for better performance
   CREATE INDEX idx_gmail_accounts_email ON gmail_accounts(email);
   CREATE INDEX idx_instagram_accounts_status ON instagram_accounts(status);
   CREATE INDEX idx_automation_logs_created_at ON automation_logs(created_at);
   ```

### Troubleshooting

#### Connection Issues
```python
# Test database connection
try:
    session = db_manager.get_session()
    session.execute("SELECT 1")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### Data Integrity
```python
# Check for orphaned records
from database import db_manager
session = db_manager.get_session()

# Find accounts without corresponding Gmail accounts
orphaned = session.execute("""
    SELECT ia.* FROM instagram_accounts ia
    LEFT JOIN gmail_accounts ga ON ia.email = ga.email
    WHERE ga.email IS NULL
""").fetchall()
```

## 🔒 Security Considerations

### Database Security

1. **Connection Security**
   - Use SSL connections
   - Encrypt sensitive data
   - Implement connection pooling

2. **Access Control**
   - Use dedicated database user
   - Limit permissions
   - Monitor access logs

3. **Data Protection**
   - Encrypt passwords and secrets
   - Regular backups
   - Secure credential storage

### Environment Variables

```bash
# Secure database configuration
DATABASE_URL=postgresql://user:password@host:port/db?sslmode=require
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

## 📈 Performance Optimization

### Connection Pooling

```python
# Optimize connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=3600
)
```

### Query Optimization

```python
# Use efficient queries
def get_recent_accounts(limit=100):
    session = db_manager.get_session()
    accounts = session.query(InstagramAccount)\
        .order_by(InstagramAccount.created_at.desc())\
        .limit(limit)\
        .all()
    session.close()
    return accounts
```

## 🎯 Migration Checklist

- [ ] PostgreSQL database created
- [ ] Environment variables updated
- [ ] Database dependencies installed
- [ ] Code updated to use database
- [ ] Database tables created
- [ ] Gmail accounts migrated
- [ ] Bot state migrated
- [ ] Testing completed
- [ ] Performance optimized
- [ ] Monitoring implemented
- [ ] Backup strategy in place

## 🆘 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check database URL
   - Verify network connectivity
   - Check firewall settings

2. **Authentication Failed**
   - Verify username/password
   - Check database permissions
   - Test connection manually

3. **Table Not Found**
   - Run database initialization
   - Check table creation logs
   - Verify schema permissions

### Debug Commands

```bash
# Test database connection
python -c "from database import db_manager; print(db_manager.test_connection())"

# Check database status
python db_init.py status

# View recent logs
python -c "from database import DatabaseUtils; print(DatabaseUtils.get_recent_logs(10))"
```

---

**Migration Complete!** 🎉

Your Instagram automation system now uses PostgreSQL for persistent, scalable data storage with full ACID compliance and advanced querying capabilities.
