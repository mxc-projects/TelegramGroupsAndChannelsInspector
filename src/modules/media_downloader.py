#!/usr/bin/env python3
"""
Media downloader module for Telegram Group Inspector
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from ..config.config import config, logger


class MediaDownloader:
    """Downloads media from Telegram groups and channels"""
    
    def __init__(self, client, fs_manager):
        self.client = client
        self.fs_manager = fs_manager
        self.media_limit = config.default_media_limit
        self.console = Console()
    
    async def download_group_media(self, entity, media_types=None, limit=1000, days_back=None):
        """Download media from a group"""
        logger.info(f"Downloading media from group: {entity.title}")
        self.console.print(Panel(
            f"[bold cyan]Downloading media from:[/] [bold white]{entity.title}[/]",
            border_style="blue",
            title="Media Downloader"
        ))
        
        # Get days back from user if not provided
        if days_back is None:
            days_input = input("Enter number of days back to download media (default: all media): ")
            if days_input.strip() and days_input.isdigit():
                days_back = int(days_input)
                self.console.print(f"[green]Downloading media from the last {days_back} days...[/]")
            else:
                days_back = 0
                self.console.print("[green]Downloading all available media...[/]")
        
        # Calculate date limit if days_back is specified
        date_limit = None
        if days_back > 0:
            date_limit = datetime.now() - timedelta(days=days_back)
            logger.info(f"Setting date limit to: {date_limit}")
        
        if not media_types:
            media_types = ["photo", "video", "document"]
            
        media_types_display = ", ".join([f"[bold cyan]{m}[/]" for m in media_types])
        self.console.print(f"Media types to download: {media_types_display}")
        
        # Get or create output directory
        output_dir = self.fs_manager.get_entity_output_dir(entity)
        media_dir = output_dir / "media"
        media_dir.mkdir(exist_ok=True)
        
        # Create directories for each media type
        type_dirs = {}
        for media_type in media_types:
            type_dir = media_dir / media_type
            type_dir.mkdir(exist_ok=True)
            type_dirs[media_type] = type_dir
        
        # First, count the total number of media files to download
        self.console.print(Panel("[bold blue]Scanning for media files...[/]", border_style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.completed} of {task.total:,} messages scanned"),
            TimeRemainingColumn(),
            expand=True
        ) as progress:
            scan_task = progress.add_task("[cyan]Scanning messages...", total=limit)
            
            media_messages = []
            message_count = 0
            
            # Collect messages that match criteria
            async for message in self.client.iter_messages(entity, limit=limit):
                message_count += 1
                progress.update(scan_task, completed=message_count)
                
                # Skip messages outside date range
                if date_limit and message.date and message.date < date_limit:
                    continue
                
                if message.media:
                    media_type = self._get_media_type(message.media)
                    if media_type in media_types:
                        media_messages.append(message)
            
            # Update progress bar with final count
            progress.update(scan_task, total=message_count, completed=message_count)
            
        total_media = len(media_messages)
        
        if total_media > 0:
            media_breakdown = {}
            for message in media_messages:
                media_type = self._get_media_type(message.media)
                media_breakdown[media_type] = media_breakdown.get(media_type, 0) + 1
            
            breakdown_str = ", ".join([f"[bold cyan]{mtype}[/]: [bold]{count}[/]" 
                                    for mtype, count in media_breakdown.items()])
            self.console.print(f"[bold green]✓[/] Found [bold]{total_media}[/] media files to download ({breakdown_str}).")
        else:
            self.console.print("[bold yellow]⚠[/] No media files found matching your criteria.")
            return None
        
        # Download media
        downloaded_files = []
        if total_media > 0:
            self.console.print(Panel("[bold blue]Starting download...[/]", border_style="blue"))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[cyan]{task.completed}/{task.total}"),
                DownloadColumn(),
                TimeRemainingColumn(),
            ) as progress:
                download_task = progress.add_task("[cyan]Downloading media", total=total_media)
                
                # Add tasks for each media type
                type_tasks = {}
                for media_type in media_types:
                    count = sum(1 for msg in media_messages if self._get_media_type(msg.media) == media_type)
                    if count > 0:
                        task_id = progress.add_task(f"[green]{media_type.capitalize()}", total=count)
                        type_tasks[media_type] = task_id
                
                for message in media_messages:
                    media_type = self._get_media_type(message.media)
                    
                    try:
                        # Create filename
                        filename = f"{entity.id}_{message.id}"
                        if hasattr(message.media, 'document') and message.media.document.attributes:
                            for attr in message.media.document.attributes:
                                if hasattr(attr, 'file_name') and attr.file_name:
                                    filename = attr.file_name
                                    break
                        
                        # Add file extension if needed
                        mime_type = self._get_mime_type(message.media)
                        if mime_type and '.' not in filename:
                            ext = self._get_file_extension(mime_type)
                            filename = f"{filename}{ext}"
                        
                        # Ensure filename is valid
                        filename = self._sanitize_filename(filename)
                        
                        # Get destination directory and path
                        dest_dir = type_dirs[media_type]
                        file_path = dest_dir / filename
                        
                        # Update progress description with current file
                        progress.update(download_task, description=f"[blue]Downloading: [cyan]{filename[:30]}...")
                        
                        # Download file
                        start_time = time.time()
                        path = await self.client.download_media(message.media, file_path)
                        end_time = time.time()
                        
                        if path:
                            download_time = end_time - start_time
                            file_size = os.path.getsize(path)
                            file_info = {
                                'id': message.id,
                                'media_type': media_type,
                                'mime_type': mime_type,
                                'filename': filename,
                                'path': str(path),
                                'size': file_size,
                                'download_time': download_time,
                                'date': message.date.isoformat() if message.date else None
                            }
                            downloaded_files.append(file_info)
                            
                            logger.info(f"Downloaded: {filename} ({file_size} bytes)")
                        else:
                            logger.warning(f"Failed to download media from message {message.id}")
                    
                    except Exception as e:
                        logger.error(f"Error downloading media from message {message.id}: {e}")
                    
                    # Update progress bars
                    progress.update(download_task, advance=1)
                    if media_type in type_tasks:
                        progress.update(type_tasks[media_type], advance=1)
            
            # Show a quick summary of downloaded files
            self.console.print(f"[bold green]✓[/] Download complete! [bold]{len(downloaded_files)}/{total_media}[/] files downloaded successfully.")
        
        # Save summary
        if downloaded_files:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            summary = {
                'entity_id': entity.id,
                'entity_title': entity.title,
                'download_date': datetime.now().isoformat(),
                'total_files': len(downloaded_files),
                'media_types': {media_type: sum(1 for file in downloaded_files if file['media_type'] == media_type) 
                              for media_type in media_types},
                'files': downloaded_files
            }
            
            summary_file = media_dir / f"download_summary_{timestamp}.json"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            # Generate HTML report
            html_content = self._generate_html_report(entity, downloaded_files, media_dir, timestamp)
            html_file = media_dir / f"media_report_{timestamp}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create a more detailed summary table
            table = Table(title=f"Media Download Summary for {entity.title}", box=box.ROUNDED)
            table.add_column("Media Type", style="cyan")
            table.add_column("Count", style="magenta", justify="right")
            table.add_column("Size", style="green", justify="right")
            
            # Calculate totals by type
            type_stats = {}
            for file in downloaded_files:
                media_type = file['media_type']
                if media_type not in type_stats:
                    type_stats[media_type] = {'count': 0, 'size': 0}
                type_stats[media_type]['count'] += 1
                type_stats[media_type]['size'] += file.get('size', 0)
            
            # Add rows for each media type
            for media_type, stats in type_stats.items():
                size_mb = stats['size'] / (1024 * 1024)
                table.add_row(
                    media_type.capitalize(),
                    str(stats['count']),
                    f"{size_mb:.2f} MB"
                )
            
            # Add total row
            total_size_mb = sum(stats['size'] for stats in type_stats.values()) / (1024 * 1024)
            table.add_row(
                "Total", 
                str(len(downloaded_files)), 
                f"{total_size_mb:.2f} MB",
                style="bold white on blue"
            )
            
            self.console.print("\n")
            self.console.print(table)
            self.console.print("\n")
            
            self.console.print(Panel(
                f"[bold green]✓[/] Downloaded [bold]{len(downloaded_files)}[/] files\n"
                f"[cyan]Files saved to:[/] [white]{media_dir}[/]\n"
                f"[cyan]Summary file:[/] [white]{summary_file.name}[/]\n"
                f"[cyan]HTML report:[/] [white]{html_file.name}[/]",
                title="Download Complete",
                border_style="green"
            ))
            
            return {
                'status': 'success',
                'entity_id': entity.id,
                'total_files': len(downloaded_files),
                'output_dir': str(media_dir),
                'summary_file': str(summary_file),
                'html_report': str(html_file)
            }
        else:
            self.console.print(Panel("[bold red]❌ No media files found or downloaded[/]", border_style="red"))
            return None
    
    async def download_channel_media(self, entity, media_types=None, limit=1000, days_back=None):
        """Download media from a channel"""
        # For channels, we'll use the same method as for groups
        return await self.download_group_media(entity, media_types, limit, days_back)
    
    def _generate_html_report(self, entity, downloaded_files, media_dir, timestamp):
        """Generate an HTML report for downloaded media"""
        # Group files by media type
        files_by_type = {}
        for file in downloaded_files:
            media_type = file['media_type']
            if media_type not in files_by_type:
                files_by_type[media_type] = []
            files_by_type[media_type].append(file)
            
        # Calculate stats
        total_size = sum(file.get('size', 0) for file in downloaded_files)
        total_size_mb = total_size / (1024 * 1024)
        
        # Create relative paths for HTML links
        for file in downloaded_files:
            file['rel_path'] = str(Path(file['path']).relative_to(media_dir.parent))
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Download Report - {entity.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #4a69bd; padding-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #4a69bd; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4a69bd; color: white; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .tab-container {{ margin: 20px 0; }}
        .tab-buttons {{ display: flex; margin-bottom: 20px; }}
        .tab-button {{ background: #f8f9fa; border: none; padding: 10px 20px; cursor: pointer; border-bottom: 2px solid transparent; }}
        .tab-button.active {{ background: #4a69bd; color: white; border-bottom: 2px solid #4a69bd; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .pagination {{ display: flex; justify-content: center; margin: 20px 0; }}
        .pagination button {{ background: #4a69bd; color: white; border: none; padding: 10px 15px; margin: 0 5px; border-radius: 5px; cursor: pointer; }}
        .image-gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }}
        .image-item {{ position: relative; overflow: hidden; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }}
        .image-item img {{ width: 100%; height: 200px; object-fit: cover; }}
        .image-item .overlay {{ position: absolute; bottom: 0; left: 0; right: 0; background-color: rgba(0,0,0,0.7); color: white; padding: 5px; font-size: 0.8em; }}
        .file-icon {{ width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; font-size: 2em; color: #4a69bd; }}
    </style>
    <script>
        function showTab(tabId) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(button => {{
                button.classList.remove('active');
            }});
            document.querySelector('[data-tab="' + tabId + '"]').classList.add('active');
        }}
        
        function filterFiles() {{
            const input = document.getElementById('fileSearch');
            const filter = input.value.toLowerCase();
            const rows = document.querySelectorAll('#filesTable tbody tr');
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }});
        }}
        
        window.onload = function() {{
            // Initialize with first tab
            showTab('all-tab');
        }};
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📥 Media Download Report</h1>
            <h2>{entity.title}</h2>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(downloaded_files)}</div>
                <div>Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(files_by_type)}</div>
                <div>Media Types</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_size_mb:.2f} MB</div>
                <div>Total Size</div>
            </div>
        </div>
        
        <div class="tab-container">
            <div class="tab-buttons">
                <button class="tab-button active" data-tab="all-tab" onclick="showTab('all-tab')">All Files</button>
                """
        
        # Add tab button for each media type
        for media_type in files_by_type:
            html_content += f"""
                <button class="tab-button" data-tab="{media_type}-tab" onclick="showTab('{media_type}-tab')">{media_type.capitalize()}</button>"""
        
        html_content += """
            </div>
            
            <div id="all-tab" class="tab-content active">
                <h2>📋 All Downloaded Files</h2>
                <input type="text" id="fileSearch" class="search-box" placeholder="Search files..." onkeyup="filterFiles()">
                <table id="filesTable">
                    <thead>
                        <tr>
                            <th>Filename</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add all files to table
        for file in downloaded_files:
            size_kb = file.get('size', 0) / 1024
            date_str = file.get('date', '').split('T')[0] if file.get('date') else 'Unknown'
            
            html_content += f"""
                        <tr>
                            <td>{file['filename']}</td>
                            <td>{file['media_type'].capitalize()}</td>
                            <td>{size_kb:.1f} KB</td>
                            <td>{date_str}</td>
                            <td><a href="{file['rel_path']}" target="_blank">Open</a></td>
                        </tr>"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
        """
        
        # Add tab content for each media type
        for media_type, files in files_by_type.items():
            html_content += f"""
            <div id="{media_type}-tab" class="tab-content">
                <h2>📂 {media_type.capitalize()} Files</h2>
            """
            
            # For photos, show a gallery
            if media_type == 'photo':
                html_content += """
                <div class="image-gallery">
                """
                for file in files:
                    html_content += f"""
                    <div class="image-item">
                        <a href="{file['rel_path']}" target="_blank">
                            <img src="{file['rel_path']}" alt="{file['filename']}">
                            <div class="overlay">{file['filename']}</div>
                        </a>
                    </div>
                    """
                html_content += """
                </div>
                """
            # For videos, show thumbnails with play button
            elif media_type == 'video':
                html_content += """
                <div class="image-gallery">
                """
                for file in files:
                    html_content += f"""
                    <div class="image-item">
                        <a href="{file['rel_path']}" target="_blank">
                            <div class="file-icon">▶️</div>
                            <div class="overlay">{file['filename']}</div>
                        </a>
                    </div>
                    """
                html_content += """
                </div>
                """
            # For other types, show a table
            else:
                html_content += """
                <table>
                    <thead>
                        <tr>
                            <th>Filename</th>
                            <th>Size</th>
                            <th>Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for file in files:
                    size_kb = file.get('size', 0) / 1024
                    date_str = file.get('date', '').split('T')[0] if file.get('date') else 'Unknown'
                    
                    html_content += f"""
                        <tr>
                            <td>{file['filename']}</td>
                            <td>{size_kb:.1f} KB</td>
                            <td>{date_str}</td>
                            <td><a href="{file['rel_path']}" target="_blank">Open</a></td>
                        </tr>"""
                
                html_content += """
                    </tbody>
                </table>
                """
            
            html_content += """
            </div>
            """
        
        html_content += """
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _get_media_type(self, media):
        """Determine media type from Telegram media object"""
        if hasattr(media, 'photo'):
            return 'photo'
        elif hasattr(media, 'document'):
            doc = media.document
            if hasattr(doc, 'mime_type'):
                if doc.mime_type.startswith('image/'):
                    return 'photo'
                elif doc.mime_type.startswith('video/'):
                    return 'video'
                elif doc.mime_type.startswith('audio/'):
                    return 'audio'
            return 'document'
        else:
            return 'document'
    
    def _get_mime_type(self, media):
        """Get mime type from media if available"""
        if hasattr(media, 'document') and hasattr(media.document, 'mime_type'):
            return media.document.mime_type
        return None
    
    def _get_file_extension(self, mime_type):
        """Get file extension from mime type"""
        if not mime_type:
            return ''
            
        mime_to_ext = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'video/mp4': '.mp4',
            'video/avi': '.avi',
            'audio/mpeg': '.mp3',
            'audio/ogg': '.ogg',
            'application/pdf': '.pdf'
        }
        
        return mime_to_ext.get(mime_type, '')
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to be valid on the file system"""
        # Remove invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Truncate if too long
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:195] + ext
        
        return filename

