#!/usr/bin/env python3
"""
User scanner module for Telegram Group Inspector
"""

from datetime import datetime, timedelta

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from telethon.tl.types import Channel, Chat

from ..config.config import logger
from ..units.file_manager import FileSystemManager


class UserScanner:
    """Scanner for individual users across all groups"""
    
    def __init__(self, client):
        """Initialize the user scanner"""
        self.client = client
        self.fs_manager = FileSystemManager()
        self.console = Console()
    
    async def scan_user_across_groups(self, target_user_input, days_back=None):
        """Scan specific user across all accessible groups"""
        logger.info(f"Scanning user: {target_user_input}")
        
        # Get days back from user if not provided
        if days_back is None:
            days_input = input("Enter number of days back to scan (default: all time): ")
            if days_input.strip() and days_input.isdigit():
                days_back = int(days_input)
                self.console.print(f"[green]Scanning messages from the last {days_back} days...[/]")
            else:
                days_back = 0
                self.console.print("[green]Scanning all available messages...[/]")
        
        # Calculate date limit if days_back is specified
        date_limit = None
        if days_back > 0:
            date_limit = datetime.now() - timedelta(days=days_back)
            logger.info(f"Setting date limit to: {date_limit}")
        
        # Try to resolve user
        try:
            if target_user_input.isdigit():
                target_user = await self.client.get_entity(int(target_user_input))
            else:
                target_user = await self.client.get_entity(target_user_input)
                
            self.console.print(Panel(
                f"[bold cyan]User found:[/] [bold white]{target_user.first_name} {target_user.last_name or ''}[/]\n"
                f"[cyan]Username:[/] [white]@{target_user.username or 'N/A'}[/]\n"
                f"[cyan]User ID:[/] [white]{target_user.id}[/]",
                title="User Information",
                border_style="blue"
            ))
            
            logger.info(f"Found user: {target_user.first_name} (@{target_user.username}) - ID: {target_user.id}")
        except Exception as e:
            logger.error(f"Could not find user: {e}")
            self.console.print(f"[bold red]Error:[/] Could not find user - {e}")
            return None
        
        # Get or create user directory
        user_dir = self.fs_manager.get_entity_output_dir(target_user)
        
        all_user_messages = []
        groups_found = []
        
        self.console.print("[yellow]Scanning all accessible groups and channels. This may take some time...[/]")
        
        # Initialize progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold cyan]{task.fields[group]}[/]"),
            TextColumn("[green]{task.completed} of {task.total} groups processed"),
            TimeElapsedColumn(),
            expand=True
        ) as progress:
            # Count total dialogs first
            dialog_count = 0
            async for _ in self.client.iter_dialogs():
                dialog_count += 1
                
            scan_task = progress.add_task(
                "[cyan]Scanning groups...", 
                total=dialog_count,
                group="",
                completed=0
            )
            
            message_count = 0
            processed = 0
            
            # Scan all groups and channels
            async for dialog in self.client.iter_dialogs():
                processed += 1
                progress.update(scan_task, completed=processed, group=dialog.name)
                
                if isinstance(dialog.entity, (Channel, Chat)):
                    try:
                        logger.info(f"Scanning: {dialog.name}")
                        
                        group_messages = []
                        async for message in self.client.iter_messages(dialog.entity, limit=5000):
                            # Skip messages outside date range if a limit is set
                            if date_limit and message.date and message.date < date_limit:
                                continue
                            
                            if (message.from_id and 
                                hasattr(message.from_id, 'user_id') and 
                                message.from_id.user_id == target_user.id and 
                                message.text):
                                
                                msg_data = {
                                    'id': message.id,
                                    'text': message.text,
                                    'date': message.date.isoformat() if message.date else None,
                                    'group_name': dialog.name,
                                    'group_id': dialog.id,
                                    'reply_to': message.reply_to_msg_id if message.reply_to else None
                                }
                                group_messages.append(msg_data)
                                all_user_messages.append(msg_data)
                                message_count += 1
                        
                        if group_messages:
                            groups_found.append({
                                'group_name': dialog.name,
                                'group_id': dialog.id,
                                'message_count': len(group_messages)
                            })
                            logger.info(f"Found {len(group_messages)} messages in {dialog.name}")
                    
                    except Exception as e:
                        logger.warning(f"Could not scan {dialog.name}: {e}")
                        continue
        
        if not all_user_messages:
            self.console.print("[bold yellow]No messages found for this user in accessible groups[/]")
            logger.warning("No messages found for this user in accessible groups")
            return None
        
        # Display summary before saving
        self._display_groups_summary(groups_found)
        
        # Save results
        self.console.print("[cyan]Saving scan results...[/]")
        result = await self._save_user_scan_results(target_user, all_user_messages, groups_found, user_dir)
        
        self.console.print(Panel(
            f"[bold green]✅ Scan complete![/]\n"
            f"[cyan]Found:[/] [white]{len(all_user_messages)} messages in {len(groups_found)} groups[/]\n"
            f"[cyan]Results saved to:[/] [white]{result['files']['html']}[/]",
            border_style="green"
        ))
        
        logger.info(f"Scan complete: {len(all_user_messages)} messages found in {len(groups_found)} groups")
        return result
    
    def _display_groups_summary(self, groups):
        """Display a table of groups where user was found"""
        if not groups:
            return
            
        table = Table(
            title="Groups Where User Was Found",
            title_style="bold cyan",
            box=ROUNDED,
            border_style="blue", 
            header_style="bold cyan",
            show_header=True
        )
        
        # Add columns
        table.add_column("Group Name", style="white")
        table.add_column("Group ID", style="cyan")
        table.add_column("Messages", style="green", justify="right")
        
        # Sort by message count
        sorted_groups = sorted(groups, key=lambda x: x['message_count'], reverse=True)
        
        for group in sorted_groups:
            table.add_row(
                group['group_name'],
                str(group['group_id']),
                str(group['message_count'])
            )
        
        self.console.print()
        self.console.print(table)
    
    async def _save_user_scan_results(self, user, messages, groups, output_dir):
        """Save user scan results in multiple formats"""
        # Create timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f"scan_{timestamp}.json"
        scan_data = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone if hasattr(user, 'phone') else None
            },
            'scan_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'groups_found': groups,
            'messages': messages
        }
        
        json_path = self.fs_manager.save_json(scan_data, user, json_file)
        
        # Save as text file
        txt_file = f"messages_{timestamp}.txt"
        text_content = self._generate_text_report(user, messages, groups)
        text_path = self.fs_manager.save_text(text_content, user, txt_file)
        
        # Generate HTML report
        html_file = f"report_{timestamp}.html"
        html_content = self._generate_html_report(user, messages, groups)
        html_path = self.fs_manager.save_html(html_content, user, html_file)
        
        # Create summary
        summary = {
            'user_id': user.id,
            'username': user.username,
            'scan_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'groups_count': len(groups),
            'files': {
                'json': json_path,
                'text': text_path,
                'html': html_path
            }
        }
        
        return summary
    
    def _generate_text_report(self, user, messages, groups):
        """Generate text report of user messages"""
        text = "USER SCAN REPORT\n"
        text += "================\n\n"
        text += f"User: {user.first_name} {user.last_name or ''} (@{user.username})\n"
        text += f"User ID: {user.id}\n"
        text += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"Total Messages Found: {len(messages)}\n"
        text += f"Groups Found: {len(groups)}\n\n"
        
        text += "GROUPS SUMMARY:\n"
        text += "-" * 50 + "\n"
        for group in sorted(groups, key=lambda x: x['message_count'], reverse=True):
            text += f"• {group['group_name']} ({group['group_id']}): {group['message_count']} messages\n"
        
        text += "\n\nALL MESSAGES:\n"
        text += "=" * 50 + "\n\n"
        
        # Sort messages by date
        sorted_messages = sorted(messages, key=lambda x: x['date'] or '', reverse=True)
        
        for msg in sorted_messages:
            date_str = msg['date'][:16] if msg['date'] else 'Unknown date'
            text += f"[{date_str}] {msg['group_name']}\n"
            text += f"Message ID: {msg['id']}\n"
            text += f"Text: {msg['text']}\n"
            text += "-" * 30 + "\n\n"
        
        return text
    
    def _generate_html_report(self, user, messages, groups):
        """Generate HTML report for user scan"""
        sorted_messages = sorted(messages, key=lambda x: x['date'] or '', reverse=True)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Scan Report - {user.first_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #4a69bd; padding-bottom: 20px; }}
        .user-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #4a69bd; border-left: 4px solid #4a69bd; padding-left: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #4a69bd; }}
        .message {{ background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 10px 0; }}
        .message-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9em; color: #666; }}
        .group-name {{ color: #4a69bd; font-weight: bold; }}
        .date {{ color: #888; }}
        .message-text {{ line-height: 1.5; white-space: pre-wrap; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4a69bd; color: white; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
    <script>
        function filterMessages() {{
            const input = document.getElementById('messageSearch');
            const filter = input.value.toLowerCase();
            const messages = document.getElementsByClassName('message');
            
            for (let i = 0; i < messages.length; i++) {{
                const text = messages[i].textContent.toLowerCase();
                messages[i].style.display = text.includes(filter) ? 'block' : 'none';
            }}
        }}
        
        function filterGroups() {{
            const input = document.getElementById('groupSearch');
            const filter = input.value.toLowerCase();
            const rows = document.querySelectorAll('#groupsTable tbody tr');
            
            for (let i = 0; i < rows.length; i++) {{
                const text = rows[i].textContent.toLowerCase();
                rows[i].style.display = text.includes(filter) ? '' : 'none';
            }}
        }}
        
        window.onload = function() {{
            document.getElementById('showAllBtn').addEventListener('click', function() {{
                const messages = document.getElementsByClassName('message');
                for (let i = 0; i < messages.length; i++) {{
                    messages[i].style.display = 'block';
                }}
                document.getElementById('messageSearch').value = '';
            }});
        }};
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 User Scan Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="user-info">
            <h2>User Information</h2>
            <p><strong>Name:</strong> {user.first_name} {user.last_name or ''}</p>
            <p><strong>Username:</strong> @{user.username or 'N/A'}</p>
            <p><strong>User ID:</strong> {user.id}</p>
            <p><strong>Phone:</strong> {getattr(user, 'phone', 'N/A') or 'N/A'}</p>
        </div>
        
        <div class="section">
            <h2>📈 Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(messages)}</div>
                    <div>Total Messages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(groups)}</div>
                    <div>Groups Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(set(msg['group_id'] for msg in messages))}</div>
                    <div>Unique Groups</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Groups Summary</h2>
            <input type="text" id="groupSearch" class="search-box" placeholder="Search groups..." onkeyup="filterGroups()">
            <table id="groupsTable">
                <thead>
                    <tr>
                        <th>Group Name</th>
                        <th>Group ID</th>
                        <th>Messages Found</th>
                        <th>% of Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for group in sorted(groups, key=lambda x: x['message_count'], reverse=True):
            percentage = (group['message_count'] / len(messages)) * 100 if messages else 0
            html_content += f"""
                    <tr>
                        <td>{group['group_name']}</td>
                        <td>{group['group_id']}</td>
                        <td>{group['message_count']}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>💬 All Messages</h2>
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <input type="text" id="messageSearch" class="search-box" placeholder="Search messages..." onkeyup="filterMessages()" style="flex: 1;">
                <button id="showAllBtn" style="padding: 10px; background: #4a69bd; color: white; border: none; border-radius: 5px; cursor: pointer;">Show All</button>
            </div>
        """
        
        for msg in sorted_messages:
            date_str = msg['date'][:16] if msg['date'] else 'Unknown date'
            
            html_content += f"""
            <div class="message">
                <div class="message-header">
                    <span class="group-name">{msg['group_name']}</span>
                    <span class="date">{date_str}</span>
                </div>
                <div class="message-text">{msg['text']}</div>
            </div>
            """
        
        html_content += """
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
