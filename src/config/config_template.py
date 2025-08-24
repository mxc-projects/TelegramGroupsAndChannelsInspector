#!/usr/bin/env python3
"""
Configuration Template for Telegram Groups Inspector
Copy this file to config.py and fill in your actual values
"""

# ========================
# TELEGRAM API CREDENTIALS
# ========================
# Get these from https://my.telegram.org
API_ID = "YOUR_API_ID_HERE"  # Your API ID (integer or string)
API_HASH = "YOUR_API_HASH_HERE"  # Your API Hash (string)
PHONE_NUMBER = "+1234567890"  # Your phone number with country code

# ========================
# BOT CONFIGURATION
# ========================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Optional: Bot token if using bot mode
SESSION_NAME = "INSPECTOR_BOT_SESSION"  # Session file name

# ========================
# APPLICATION SETTINGS
# ========================
APP_NAME = "Telegram Groups Inspector"
APP_VERSION = "2.0.0"
DEVELOPER = "MXC-Projects"

# ========================
# THREADING CONFIGURATION
# ========================
MAX_WORKERS = 4  # Maximum number of worker threads
BATCH_SIZE = 100  # Batch size for processing
RATE_LIMIT_DELAY = 1.0  # Delay between API calls (seconds)
ENABLE_MULTITHREADING = True  # Enable/disable multithreading

# ========================
# FILE MANAGEMENT
# ========================
BASE_OUTPUT_DIR = "src/outputs"  # Base directory for outputs
LOGS_DIR = "src/logs"  # Directory for log files
SESSIONS_DIR = "src/sessions"  # Directory for session files

# Auto-create directories if they don't exist
AUTO_CREATE_DIRS = True

# ========================
# OUTPUT FORMATS
# ========================
DEFAULT_OUTPUT_FORMAT = "json"  # Default export format
SUPPORTED_FORMATS = ["json", "csv", "txt"]  # Supported export formats
AUTO_SAVE = True  # Auto-save results
TIMESTAMP_FILES = True  # Add timestamp to output files

# ========================
# LOGGING CONFIGURATION
# ========================
LOG_LEVEL = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_LOG_SIZE = 10 * 1024 * 1024  # Max log file size (10MB)
LOG_BACKUP_COUNT = 5  # Number of backup log files

# ========================
# SECURITY SETTINGS
# ========================
ENCRYPT_SESSIONS = True  # Encrypt session files
SECURE_DELETE = True  # Secure deletion of temporary files
PRIVACY_MODE = True  # Enable privacy protections

# ========================
# PERFORMANCE SETTINGS
# ========================
CHUNK_SIZE = 1024  # File chunk size for processing
TIMEOUT = 30  # Request timeout (seconds)
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed operations
RETRY_DELAY = 2  # Delay between retry attempts (seconds)

# ========================
# UI CONFIGURATION
# ========================
ENABLE_EMOJI = True  # Enable emoji in UI
ENABLE_COLORS = True  # Enable colored output
PROGRESS_BAR = True  # Show progress bars
CONSOLE_WIDTH = 80  # Console width for formatting

# ========================
# DOWNLOAD SETTINGS
# ========================
MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024  # Max file size for download (100MB)
DOWNLOAD_TIMEOUT = 300  # Download timeout (seconds)
ORGANIZE_BY_DATE = True  # Organize downloads by date
CREATE_THUMBNAILS = False  # Create thumbnails for images

# ========================
# MESSAGE FILTERING
# ========================
FILTER_DELETED_MESSAGES = True  # Filter out deleted messages
FILTER_EMPTY_MESSAGES = True  # Filter out empty messages
MAX_MESSAGE_LENGTH = 4096  # Maximum message length to process

# ========================
# GROUP SCANNING
# ========================
SCAN_DELETED_USERS = False  # Include deleted users in scans
SCAN_BOTS = True  # Include bots in user scans
MAX_MEMBERS_SCAN = 10000  # Maximum members to scan per group

# ========================
# DATABASE SETTINGS (Optional)
# ========================
# Uncomment and configure if using database storage
# DATABASE_URL = "sqlite:///telegram_inspector.db"
# DB_POOL_SIZE = 5
# DB_MAX_OVERFLOW = 10

# ========================
# NOTIFICATION SETTINGS
# ========================
SEND_COMPLETION_NOTIFICATION = False  # Send notification when tasks complete
NOTIFICATION_CHAT_ID = None  # Chat ID for notifications

# ========================
# ADVANCED SETTINGS
# ========================
DEBUG_MODE = False  # Enable debug mode
VERBOSE_LOGGING = False  # Enable verbose logging
PROFILE_PERFORMANCE = False  # Enable performance profiling

# ========================
# CUSTOM SETTINGS
# ========================
# Add your custom configuration here
CUSTOM_USER_AGENT = "TelegramGroupsInspector/2.0"
ENABLE_EXPERIMENTAL_FEATURES = False


# ========================
# VALIDATION
# ========================
def validate_config():
    """Validate configuration settings"""
    errors = []

    if API_ID == "YOUR_API_ID_HERE":
        errors.append("API_ID not configured")

    if API_HASH == "YOUR_API_HASH_HERE":
        errors.append("API_HASH not configured")

    if PHONE_NUMBER == "+1234567890":
        errors.append("PHONE_NUMBER not configured")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

    return True


# ========================
# ENVIRONMENT OVERRIDES
# ========================
import os

# Override settings from environment variables if present
API_ID = os.getenv("TELEGRAM_API_ID", API_ID)
API_HASH = os.getenv("TELEGRAM_API_HASH", API_HASH)
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE", PHONE_NUMBER)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)

# Development vs Production settings
if os.getenv("ENVIRONMENT") == "development":
    DEBUG_MODE = True
    LOG_LEVEL = "DEBUG"
    VERBOSE_LOGGING = True
