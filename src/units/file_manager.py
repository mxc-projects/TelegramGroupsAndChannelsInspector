#!/usr/bin/env python3
"""
File System Manager for Telegram Group Inspector
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from ..config.config import config, logger


class FileSystemManager:
    """Manages file system operations for the application"""

    def __init__(self):
        """Initialize the file system manager"""
        self.output_dir = config.output_dir
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all required directories exist"""
        # Make sure the base output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_entity_output_dir(self, entity):
        """Get output directory for a specific entity (group/channel/user)"""
        # Create a directory name using entity title/name and ID
        if hasattr(entity, "title") and entity.title:
            dir_name = f"{entity.title.replace('/', '_')}_{entity.id}"
        elif hasattr(entity, "username") and entity.username:
            dir_name = f"{entity.username}_{entity.id}"
        else:
            dir_name = f"entity_{entity.id}"

        # Create full path
        entity_dir = self.output_dir / dir_name
        entity_dir.mkdir(exist_ok=True)

        return entity_dir

    def get_media_dir(self, entity_dir, media_type):
        """Get media directory for a specific type"""
        media_dir = entity_dir / media_type
        media_dir.mkdir(exist_ok=True)
        return media_dir

    def save_json(self, data, entity, filename):
        """Save data as JSON file"""
        entity_dir = self.get_entity_output_dir(entity)
        file_path = entity_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved JSON to {file_path}")
        return str(file_path)

    def save_text(self, content: str, entity, filename: str) -> str:
        """Save plain text content in the entity's output directory."""
        out_dir = self.get_entity_output_dir(entity)
        path = Path(out_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved text to: {path}")
        return str(path)

    def save_html(self, html, entity, filename):
        """Save HTML to file"""
        entity_dir = self.get_entity_output_dir(entity)
        file_path = entity_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Saved HTML to {file_path}")
        return str(file_path)

    def save_media(self, media_data, entity, media_type, original_filename=None):
        """Save media file"""
        entity_dir = self.get_entity_output_dir(entity)
        media_dir = self.get_media_dir(entity_dir, media_type)

        # Create a unique filename if not provided
        if not original_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = "bin"  # Default extension
            original_filename = f"media_{timestamp}.{file_ext}"

        file_path = media_dir / original_filename

        # Save binary data
        with open(file_path, "wb") as f:
            f.write(media_data)

        logger.info(f"Saved media to {file_path}")
        return str(file_path)

    def create_report_dirs(self, entity):
        """Create directories for reports"""
        entity_dir = self.get_entity_output_dir(entity)
        reports_dir = entity_dir / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Create subdirectories for different report types
        analysis_dir = reports_dir / "analysis"
        users_dir = reports_dir / "users"
        media_dir = reports_dir / "media"

        analysis_dir.mkdir(exist_ok=True)
        users_dir.mkdir(exist_ok=True)
        media_dir.mkdir(exist_ok=True)

        return {
            "base": str(reports_dir),
            "analysis": str(analysis_dir),
            "users": str(users_dir),
            "media": str(media_dir),
        }
