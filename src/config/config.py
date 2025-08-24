#!/usr/bin/env python3
"""
Configuration module for Telegram Group Inspector
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Configuration loader with path management"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.src_dir = self.base_dir / "src"
        self.config_path = self.src_dir / "config" / ".env"

        # Load environment variables
        load_dotenv(self.config_path)

        # Telegram API settings - CONFIGURE THESE WITH YOUR OWN VALUES
        self.api_id = os.getenv("API_ID", "YOUR_API_ID_HERE")
        self.api_hash = os.getenv("API_HASH", "YOUR_API_HASH_HERE")
        self.phone_number = os.getenv("PHONE_NUMBER", "YOUR_PHONE_NUMBER_HERE")
        self.session_string = os.getenv("SESSION_STRING", "telegram_session")

        # Directory paths
        self.output_dir = self.src_dir / os.getenv("OUTPUT_DIR", "src/outputs").replace(
            "src/", ""
        )
        self.log_dir = self.src_dir / os.getenv("LOG_DIR", "src/logs").replace(
            "src/", ""
        )
        self.session_dir = self.src_dir / os.getenv(
            "SESSION_DIR", "src/sessions"
        ).replace("src/", "")

        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Analysis settings
        self.default_message_limit = int(os.getenv("DEFAULT_MESSAGE_LIMIT", 1000))
        self.default_media_limit = int(os.getenv("DEFAULT_MEDIA_LIMIT", 100))

        # Session file path
        self.session_file = self.session_dir / f"{self.session_string}"

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.log_dir / "telegram_inspector.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        return logging.getLogger("TelegramInspector")


# Create global config instance
config = Config()
logger = config.setup_logging()


def setup_logging():
    """Global setup_logging function for backward compatibility"""
    return config.setup_logging()
    """Global setup_logging function for backward compatibility"""
    return config.setup_logging()
