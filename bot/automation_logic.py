import time
import json
import imaplib
import email
import re
import requests
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyotp
from config import *

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_gmail_code(email_address, app_password):
    """Extract 6-digit verification code from Gmail"""
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_address, app_password)
        mail.select('inbox')
        
        # Search for Instagram verification emails
        status, messages = mail.search(None, 'FROM', 'instagram.com')
        if not messages[0]:
            return None
            
        # Get the latest email
        latest_email_id = messages[0].split()[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        
        # Parse email content
        email_body = msg_data[0][1].decode('utf-8')
        msg = email.message_from_string(email_body)
        
        # Extract verification code
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    code_match = re.search(r'\b\d{6}\b', body)
                    if code_match:
                        mail.close()
                        mail.logout()
                        return code_match.group()
        
        mail.close()
        mail.logout()
        return None
        
    except Exception as e:
        logger.error(f"Error getting Gmail code: {e}")
        return None

def get_temp_email():
    """Get temporary email from mailvn.site"""
    try:
        response = requests.get('https://mailvn.site')
        if response.status_code == 200:
            # Extract email from response (simplified - would need proper parsing)
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@mailvn\.site)', response.text)
            if email_match:
                return email_match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error getting temp email: {e}")
        return None

def download_profile_image():
    """Download AI-generated profile image"""
    try:
        # Using thispersondoesnotexist.com for AI-generated faces
        response = requests.get('https://thispersondoesnotexist.com/image')
        if response.status_code == 200:
            with open('/tmp/profile.jpg', 'wb') as f:
                f.write(response.content)
            return '/tmp/profile.jpg'
        return None
    except Exception as e:
        logger.error(f"Error downloading profile image: {e}")
        return None

def create_instagram_account(gmail_account, app_password, static_password):
    """Main function to create Instagram account"""
    driver = None
    try:
        # Initialize WebDriver
        options = Options()
        if HEADLESS_MODE:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(10)
        
        # Step 1: Instagram Signup
        logger.info("Starting Instagram signup process")
        driver.get('https://www.instagram.com/accounts/emailsignup/')
        
        # Fill signup form
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        email_field.send_keys(gmail_account)
        
        fullname_field = driver.find_element(By.NAME, "fullName")
        fullname_field.send_keys("John Doe")
        
        username_field = driver.find_element(By.NAME, "username")
        username_field.send_keys(f"user_{int(time.time())}")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(static_password)
        
        # Submit form
        signup_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        signup_button.click()
        
        # Step 2: Email Verification
        logger.info("Waiting for email verification")
        time.sleep(5)
        
        # Get verification code from Gmail
        verification_code = get_gmail_code(gmail_account, app_password)
        if not verification_code:
            raise Exception("Failed to get verification code")
        
        # Enter verification code
        code_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email_confirmation_code"))
        )
        code_field.send_keys(verification_code)
        
        # Submit verification
        verify_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        verify_button.click()
        
        # Step 3: Profile Setup
        logger.info("Setting up profile")
        time.sleep(5)
        
        # Download and upload profile picture
        profile_image_path = download_profile_image()
        if profile_image_path:
            # Upload profile picture
            file_input = driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(profile_image_path)
            time.sleep(3)
            
            # Click next
            next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(2)
            
            # Skip additional steps
            skip_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Skip')]")
            skip_button.click()
        
        # Step 4: Get final username
        final_username = driver.find_element(By.XPATH, "//h2").text
        
        # Step 5: Email Replacement
        logger.info("Replacing email with temporary email")
        
        # Get temporary email
        temp_email = get_temp_email()
        if not temp_email:
            raise Exception("Failed to get temporary email")
        
        # Navigate to settings
        driver.get('https://www.instagram.com/accounts/edit/')
        time.sleep(3)
        
        # Add temporary email (simplified - would need proper navigation)
        # This is a complex process that requires careful navigation
        
        # Step 6: 2FA Setup
        logger.info("Setting up 2FA")
        
        # Navigate to 2FA settings
        driver.get('https://www.instagram.com/accounts/two_factor_authentication/')
        time.sleep(3)
        
        # Enable 2FA with authenticator app
        auth_app_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Authentication App')]")
        auth_app_button.click()
        time.sleep(3)
        
        # Extract 2FA secret key
        secret_key_element = driver.find_element(By.XPATH, "//code")
        secret_key = secret_key_element.text
        
        # Complete 2FA setup
        confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm')]")
        confirm_button.click()
        
        # Return account data
        account_data = {
            'username': final_username,
            'temp_email': temp_email,
            'password': static_password,
            'secret_key': secret_key,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active'
        }
        
        logger.info(f"Account created successfully: {final_username}")
        return account_data
        
    except Exception as e:
        logger.error(f"Error creating Instagram account: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def save_to_google_sheets(account_data):
    """Save account data to Google Sheets"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Authenticate with Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open spreadsheet
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Append data
        row_data = [
            account_data['username'],
            account_data['temp_email'],
            account_data['password'],
            account_data['secret_key'],
            account_data['created_at'],
            account_data['status']
        ]
        
        worksheet.append_row(row_data)
        logger.info("Account data saved to Google Sheets")
        
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}")

def load_bot_state():
    """Load bot state from JSON file"""
    try:
        if os.path.exists(BOT_STATE_FILE):
            with open(BOT_STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            'is_running': False,
            'current_index': 0,
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'last_updated': None
        }
    except Exception as e:
        logger.error(f"Error loading bot state: {e}")
        return {
            'is_running': False,
            'current_index': 0,
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'last_updated': None
        }

def save_bot_state(state):
    """Save bot state to JSON file"""
    try:
        state['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(BOT_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving bot state: {e}")

def load_gmail_accounts():
    """Load Gmail accounts from file"""
    try:
        accounts = []
        with open(GMAIL_ACCOUNTS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ',' in line:
                    email, password = line.split(',', 1)
                    accounts.append({
                        'email': email.strip(),
                        'app_password': password.strip()
                    })
        return accounts
    except Exception as e:
        logger.error(f"Error loading Gmail accounts: {e}")
        return []

def load_static_password():
    """Load static password from file"""
    try:
        with open(PASSWORD_FILE, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading static password: {e}")
        return "DefaultPassword123!"
