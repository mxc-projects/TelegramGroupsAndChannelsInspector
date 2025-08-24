#!/usr/bin/env python3
"""
Group scanner module for Telegram Group Inspector
"""

from collections import Counter
from datetime import datetime, timedelta

from rich import box
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

from ..config.config import logger
from ..units.file_manager import FileSystemManager


class GroupScanner:
    """Scanner for Telegram groups and channels"""
    
    def __init__(self, client):
        """Initialize the group scanner"""
        self.client = client
        self.fs_manager = FileSystemManager()
        self.console = Console()
    
    async def scan_group_members(self, group):
        """Scan members of a specific group"""
        self.console.print(Panel.fit(f"Scanning members of group: [bold blue]{group.title}[/]", border_style="blue", title="Group Scanner"))
        
        try:
            members = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Scanning members...[/]"),
                BarColumn(),
                TextColumn("[bold]{task.completed}/{task.total}[/]"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                # We don't know how many members in advance, so we start with 100 as estimate
                scan_task = progress.add_task("[blue]Scanning members...", total=100)
                
                count = 0
                async for user in self.client.iter_participants(group):
                    if user:
                        member_data = {
                            'id': user.id,
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'phone': getattr(user, 'phone', None),
                            'is_bot': getattr(user, 'bot', False),
                            'is_premium': getattr(user, 'premium', False),
                            'date_added': datetime.now().isoformat()
                        }
                        members.append(member_data)
                    
                    count += 1
                    # Update progress, adjust total if needed
                    if count > progress.tasks[scan_task].total or 0:
                        progress.update(scan_task, total=count + 50)
                    progress.update(scan_task, completed=count)
            
            self.console.print(f"[bold green]✓[/] Found [bold]{len(members)}[/] members in [bold blue]{group.title}[/]")
            
            # Display summary table
            table = Table(title=f"Member Types in {group.title}", box=box.ROUNDED)
            table.add_column("Member Type", style="cyan")
            table.add_column("Count", style="magenta")
            
            bot_count = sum(1 for m in members if m['is_bot'])
            premium_count = sum(1 for m in members if m['is_premium'])
            regular_count = len(members) - bot_count - premium_count
            
            table.add_row("Regular Users", str(regular_count))
            table.add_row("Premium Users", str(premium_count))
            table.add_row("Bots", str(bot_count))
            table.add_row("Total", str(len(members)))
            
            self.console.print(table)
            
            # Save results
            self.console.print("[yellow]Saving results...[/]")
            result = await self._save_members_results(group, members)
            
            self.console.print(Panel.fit(
                f"[bold green]✓[/] Scan completed and saved successfully!\n\n"
                f"[bold]Files saved:[/]\n"
                f"[cyan]JSON:[/] {result['files']['json']}\n"
                f"[cyan]Text:[/] {result['files']['text']}\n"
                f"[cyan]HTML:[/] {result['files']['html']}",
                title="Scan Complete",
                border_style="green"
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error scanning group members: {e}")
            self.console.print(f"[bold red]Error scanning group members:[/] {e}")
            return None
    
    async def scan_group_messages(self, group, limit=1000, days_back=None):
        """Scan messages from a specific group"""
        self.console.print(Panel.fit(f"Scanning messages from group: [bold blue]{group.title}[/]", 
                                 border_style="blue", title="Group Scanner"))
        
        # Get days back from user if not provided
        if days_back is None:
            days_input = input("Enter number of days back to scan (default: all messages): ")
            if days_input.strip() and days_input.isdigit():
                days_back = int(days_input)
                self.console.print(f"[bold]Scanning messages from the last {days_back} days...[/]")
            else:
                days_back = 0
                self.console.print("[bold]Scanning all available messages...[/]")
        
        # Calculate date limit if days_back is specified
        date_limit = None
        if days_back > 0:
            date_limit = datetime.now() - timedelta(days=days_back)
            self.console.print(f"[yellow]Setting date limit to:[/] {date_limit}")
        
        try:
            messages = []
            users = {}
            user_message_count = Counter()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Scanning messages...[/]"),
                BarColumn(),
                TextColumn("[bold]{task.completed}/{task.total}[/]"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                scan_task = progress.add_task("[blue]Scanning messages...", total=limit)
                count = 0
                
                async for message in self.client.iter_messages(group, limit=limit):
                    # Skip messages before date_limit if it's set
                    if date_limit and message.date and message.date.replace(tzinfo=None) < date_limit:
                        logger.info(f"Reached date limit, stopping message collection at {message.date}")
                        progress.update(scan_task, completed=limit)  # Mark as complete
                        break
                    
                    if message.sender_id:
                        user_message_count[message.sender_id] += 1
                        
                        # Get user info if not already stored
                        if message.sender_id not in users:
                            try:
                                user = await self.client.get_entity(message.sender_id)
                                users[message.sender_id] = {
                                    'id': user.id,
                                    'username': user.username,
                                    'first_name': getattr(user, 'first_name', None),
                                    'last_name': getattr(user, 'last_name', None),
                                    'phone': getattr(user, 'phone', None)
                                }
                            except Exception as e:
                                logger.warning(f"Could not get user info for {message.sender_id}: {e}")
                                users[message.sender_id] = {
                                    'id': message.sender_id,
                                    'username': 'unknown',
                                    'first_name': 'Unknown',
                                    'last_name': 'User',
                                    'phone': None
                                }
                    
                    # Process message
                    msg_data = {
                        'id': message.id,
                        'date': message.date.isoformat() if message.date else None,
                        'sender_id': message.sender_id,
                        'text': message.text,
                        'has_media': message.media is not None,
                        'is_reply': message.reply_to is not None,
                        'forward': message.forward is not None,
                    }
                    
                    messages.append(msg_data)
                    count += 1
                    progress.update(scan_task, completed=count)
            
            self.console.print(f"[bold green]✓[/] Found [bold]{len(messages)}[/] messages in [bold blue]{group.title}[/]")
            
            # Display user statistics
            self.console.print("\n[bold]Top message senders:[/]")
            table = Table(title=f"Top Users in {group.title}", box=box.ROUNDED)
            table.add_column("Username", style="cyan")
            table.add_column("Messages", style="magenta", justify="right")
            table.add_column("Percentage", style="green", justify="right")
            
            # Calculate total messages for percentage
            total_messages = len(messages)
            
            # Add top 10 users to table
            for user_id, count in user_message_count.most_common(10):
                user_info = users.get(user_id, {'username': 'unknown', 'first_name': 'Unknown'})
                username = user_info.get('username') or f"{user_info.get('first_name', '')} (ID: {user_id})"
                percentage = (count / total_messages) * 100 if total_messages else 0
                table.add_row(f"@{username}", str(count), f"{percentage:.1f}%")
            
            self.console.print(table)
            
            # Save results
            self.console.print("[yellow]Saving results...[/]")
            result = await self._save_messages_results(group, messages, users, user_message_count)
            
            self.console.print(Panel.fit(
                f"[bold green]✓[/] Scan completed and saved successfully!\n\n"
                f"[bold]Files saved:[/]\n"
                f"[cyan]JSON:[/] {result['files']['json']}\n"
                f"[cyan]Text:[/] {result['files']['text']}\n"
                f"[cyan]HTML:[/] {result['files']['html']}",
                title="Scan Complete",
                border_style="green"
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error scanning group messages: {e}")
            self.console.print(f"[bold red]Error scanning group messages:[/] {e}")
            return None
    
    async def _save_members_results(self, group, members):
        """Save group members scan results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f"members_{timestamp}.json"
        members_data = {
            'group_info': {
                'id': group.id,
                'title': group.title,
                'username': getattr(group, 'username', None)
            },
            'scan_date': datetime.now().isoformat(),
            'total_members': len(members),
            'members': members
        }
        
        json_path = self.fs_manager.save_json(members_data, group, json_file)
        
        # Save as text file
        txt_file = f"members_{timestamp}.txt"
        text_content = self._generate_members_text_report(group, members)
        text_path = self.fs_manager.save_text(text_content, group, txt_file)
        
        # Generate HTML report
        html_file = f"members_report_{timestamp}.html"
        html_content = self._generate_members_html_report(group, members)
        html_path = self.fs_manager.save_html(html_content, group, html_file)
        
        return {
            'group_id': group.id,
            'group_title': group.title,
            'scan_date': datetime.now().isoformat(),
            'total_members': len(members),
            'files': {
                'json': json_path,
                'text': text_path,
                'html': html_path
            }
        }
    
    async def _save_messages_results(self, group, messages, users, user_message_count):
        """Save group messages scan results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get top users
        top_users = user_message_count.most_common(20)
        top_users_data = [{'user_id': uid, 'count': count, 'user_info': users.get(uid, {'id': uid})} 
                         for uid, count in top_users]
        
        # Save as JSON
        json_file = f"messages_{timestamp}.json"
        messages_data = {
            'group_info': {
                'id': group.id,
                'title': group.title,
                'username': getattr(group, 'username', None)
            },
            'scan_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'total_users': len(users),
            'top_users': top_users_data,
            'messages': messages
        }
        
        json_path = self.fs_manager.save_json(messages_data, group, json_file)
        
        # Save as text file
        txt_file = f"messages_{timestamp}.txt"
        text_content = self._generate_messages_text_report(group, messages, top_users_data)
        text_path = self.fs_manager.save_text(text_content, group, txt_file)
        
        # Generate HTML report
        html_file = f"messages_report_{timestamp}.html"
        html_content = self._generate_messages_html_report(group, messages, top_users_data)
        html_path = self.fs_manager.save_html(html_content, group, html_file)
        
        return {
            'group_id': group.id,
            'group_title': group.title,
            'scan_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'total_users': len(users),
            'files': {
                'json': json_path,
                'text': text_path,
                'html': html_path
            }
        }
    
    def _generate_members_text_report(self, group, members):
        """Generate text report for group members"""
        text = "GROUP MEMBERS REPORT\n"
        text += "===================\n\n"
        text += f"Group: {group.title}\n"
        text += f"Group ID: {group.id}\n"
        text += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"Total Members: {len(members)}\n\n"
        
        text += "MEMBERS LIST:\n"
        text += "-" * 50 + "\n"
        
        for member in members:
            text += f"ID: {member['id']}\n"
            text += f"Username: @{member['username'] or 'N/A'}\n"
            text += f"Name: {member['first_name'] or ''} {member['last_name'] or ''}\n"
            text += f"Phone: {member['phone'] or 'N/A'}\n"
            text += f"Bot: {'Yes' if member['is_bot'] else 'No'}\n"
            text += f"Premium: {'Yes' if member['is_premium'] else 'No'}\n"
            text += "-" * 30 + "\n"
        
        return text
    
    def _generate_messages_text_report(self, group, messages, top_users):
        """Generate text report for group messages"""
        text = "GROUP MESSAGES REPORT\n"
        text += "====================\n\n"
        text += f"Group: {group.title}\n"
        text += f"Group ID: {group.id}\n"
        text += f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"Total Messages: {len(messages)}\n\n"
        
        text += "TOP USERS BY MESSAGE COUNT:\n"
        text += "-" * 50 + "\n"
        for user in top_users:
            user_info = user['user_info']
            username = user_info.get('username', 'N/A')
            text += f"@{username}: {user['count']} messages\n"
        
        text += "\n\nRECENT MESSAGES:\n"
        text += "=" * 50 + "\n\n"
        
        # Show last 50 messages
        for msg in messages[:50]:
            date_str = msg['date'][:16] if msg['date'] else 'Unknown date'
            text += f"[{date_str}] User {msg['sender_id']}\n"
            text += f"Text: {msg['text'] or 'No text'}\n"
            text += "-" * 30 + "\n"
        
        return text
    
    def _generate_members_html_report(self, group, members):
        """Generate HTML report for group members"""
        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Members Report - {group.title}</title>
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
        .pagination {{ display: flex; justify-content: center; margin: 20px 0; }}
        .pagination button {{ background: #4a69bd; color: white; border: none; padding: 10px 15px; margin: 0 5px; border-radius: 5px; cursor: pointer; }}
        .pagination button:disabled {{ background: #cccccc; cursor: not-allowed; }}
    </style>
    <script>
        // Pagination functionality
        function setupPagination() {{
            const itemsPerPage = 25;
            const rows = document.querySelectorAll('#membersTable tbody tr');
            const pageCount = Math.ceil(rows.length / itemsPerPage);
            
            // Create pagination
            const paginationDiv = document.getElementById('pagination');
            
            // Previous button
            const prevBtn = document.createElement('button');
            prevBtn.innerText = '< Previous';
            prevBtn.addEventListener('click', function() {{
                if (currentPage > 1) showPage(currentPage - 1);
            }});
            paginationDiv.appendChild(prevBtn);
            
            // Page numbers
            for (let i = 1; i <= pageCount; i++) {{
                const pageBtn = document.createElement('button');
                pageBtn.innerText = i;
                pageBtn.addEventListener('click', function() {{
                    showPage(i);
                }});
                paginationDiv.appendChild(pageBtn);
            }}
            
            // Next button
            const nextBtn = document.createElement('button');
            nextBtn.innerText = 'Next >';
            nextBtn.addEventListener('click', function() {{
                if (currentPage < pageCount) showPage(currentPage + 1);
            }});
            paginationDiv.appendChild(nextBtn);
            
            // Show initial page
            let currentPage = 1;
            showPage(currentPage);
            
            function showPage(page) {{
                currentPage = page;
                
                // Update button states
                prevBtn.disabled = (currentPage === 1);
                nextBtn.disabled = (currentPage === pageCount);
                
                // Hide all rows
                rows.forEach(row => {{
                    row.style.display = 'none';
                }});
                
                // Show rows for current page
                const start = (page - 1) * itemsPerPage;
                const end = start + itemsPerPage;
                
                for (let i = start; i < end && i < rows.length; i++) {{
                    rows[i].style.display = '';
                }}
                
                // Update active button
                document.querySelectorAll('#pagination button').forEach((btn, index) => {{
                    if (index !== 0 && index !== pageCount + 1) {{
                        if (index === page) {{
                            btn.style.background = '#284b8c';
                        }} else {{
                            btn.style.background = '#4a69bd';
                        }}
                    }}
                }});
            }}
        }}
        
        function filterMembers() {{
            const input = document.getElementById('memberSearch');
            const filter = input.value.toLowerCase();
            const rows = document.querySelectorAll('#membersTable tbody tr');
            
            // Show all rows first (reset pagination)
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }});
            
            // Hide pagination if searching
            document.getElementById('pagination').style.display = filter ? 'none' : 'flex';
            
            // If not searching, reset pagination
            if (!filter) {{
                setupPagination();
            }}
        }}
        
        window.onload = function() {{
            setupPagination();
        }};
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 Group Members Report</h1>
            <h2>{group.title}</h2>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(members)}</div>
                <div>Total Members</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for m in members if m['is_bot'])}</div>
                <div>Bots</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for m in members if m['is_premium'])}</div>
                <div>Premium Users</div>
            </div>
        </div>
        
        <h2>📋 Members List</h2>
        <input type="text" id="memberSearch" class="search-box" placeholder="Search members..." onkeyup="filterMembers()">
        <table id="membersTable">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>ID</th>
                    <th>Phone</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for member in members:
            name = f"{member['first_name'] or ''} {member['last_name'] or ''}".strip()
            username = member['username'] or 'N/A'
            member_type = 'Bot' if member['is_bot'] else ('Premium' if member['is_premium'] else 'Regular')
            
            html_content += f"""
                <tr>
                    <td>@{username}</td>
                    <td>{name or 'N/A'}</td>
                    <td>{member['id']}</td>
                    <td>{member['phone'] or 'N/A'}</td>
                    <td>{member_type}</td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        <div id="pagination" class="pagination"></div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _generate_messages_html_report(self, group, messages, top_users):
        """Generate HTML report for group messages"""
        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messages Report - {group.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #4a69bd; padding-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #4a69bd; }}
        .message {{ background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 10px 0; }}
        .message-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9em; color: #666; }}
        .message-text {{ line-height: 1.5; white-space: pre-wrap; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4a69bd; color: white; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .pagination {{ display: flex; justify-content: center; margin: 20px 0; }}
        .pagination button {{ background: #4a69bd; color: white; border: none; padding: 10px 15px; margin: 0 5px; border-radius: 5px; cursor: pointer; }}
        .pagination button:disabled {{ background: #cccccc; cursor: not-allowed; }}
        .chart-container {{ width: 100%; max-width: 800px; margin: 0 auto; }}
        .tag-cloud {{ margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center; }}
        .tab-container {{ margin: 20px 0; }}
        .tab-buttons {{ display: flex; margin-bottom: 20px; }}
        .tab-button {{ background: #f8f9fa; border: none; padding: 10px 20px; cursor: pointer; border-bottom: 2px solid transparent; }}
        .tab-button.active {{ background: #4a69bd; color: white; border-bottom: 2px solid #4a69bd; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Pagination functionality for messages
        function setupMessagePagination() {{
            const itemsPerPage = 10;
            const messages = document.querySelectorAll('.message');
            const pageCount = Math.ceil(messages.length / itemsPerPage);
            
            // Create pagination
            const paginationDiv = document.getElementById('messagePagination');
            paginationDiv.innerHTML = '';
            
            // Previous button
            const prevBtn = document.createElement('button');
            prevBtn.innerText = '< Previous';
            prevBtn.addEventListener('click', function() {{
                if (currentPage > 1) showPage(currentPage - 1);
            }});
            paginationDiv.appendChild(prevBtn);
            
            // Page numbers (show max 5 pages with ellipsis)
            const maxPageButtons = 5;
            let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
            let endPage = Math.min(pageCount, startPage + maxPageButtons - 1);
            
            if (startPage > 1) {{
                const firstPageBtn = document.createElement('button');
                firstPageBtn.innerText = '1';
                firstPageBtn.addEventListener('click', function() {{ showPage(1); }});
                paginationDiv.appendChild(firstPageBtn);
                
                if (startPage > 2) {{
                    const ellipsisBtn = document.createElement('span');
                    ellipsisBtn.innerText = '...';
                    ellipsisBtn.style.margin = '0 10px';
                    paginationDiv.appendChild(ellipsisBtn);
                }}
            }}
            
            for (let i = startPage; i <= endPage; i++) {{
                const pageBtn = document.createElement('button');
                pageBtn.innerText = i;
                pageBtn.addEventListener('click', function() {{ showPage(i); }});
                if (i === currentPage) {{ pageBtn.style.background = '#284b8c'; }}
                paginationDiv.appendChild(pageBtn);
            }}
            
            if (endPage < pageCount) {{
                if (endPage < pageCount - 1) {{
                    const ellipsisBtn = document.createElement('span');
                    ellipsisBtn.innerText = '...';
                    ellipsisBtn.style.margin = '0 10px';
                    paginationDiv.appendChild(ellipsisBtn);
                }}
                
                const lastPageBtn = document.createElement('button');
                lastPageBtn.innerText = pageCount;
                lastPageBtn.addEventListener('click', function() {{ showPage(pageCount); }});
                paginationDiv.appendChild(lastPageBtn);
            }}
            
            // Next button
            const nextBtn = document.createElement('button');
            nextBtn.innerText = 'Next >';
            nextBtn.addEventListener('click', function() {{
                if (currentPage < pageCount) showPage(currentPage + 1);
            }});
            paginationDiv.appendChild(nextBtn);
            
            // Update button states
            prevBtn.disabled = (currentPage === 1);
            nextBtn.disabled = (currentPage === pageCount);
        }}
        
        function showPage(page) {{
            currentPage = page;
            const itemsPerPage = 10;
            const messages = document.querySelectorAll('.message');
            
            // Hide all messages
            messages.forEach(message => {{
                message.style.display = 'none';
            }});
            
            // Show messages for current page
            const start = (page - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            
            for (let i = start; i < end && i < messages.length; i++) {{
                messages[i].style.display = 'block';
            }}
            
            // Update pagination
            setupMessagePagination();
        }}
        
        function filterMessages() {{
            const input = document.getElementById('messageSearch');
            const filter = input.value.toLowerCase();
            const messages = document.querySelectorAll('.message');
            
            if (filter) {{
                // Show only matching messages
                let hasVisibleMessages = false;
                messages.forEach(message => {{
                    const text = message.textContent.toLowerCase();
                    const isVisible = text.includes(filter);
                    message.style.display = isVisible ? 'block' : 'none';
                    if (isVisible) hasVisibleMessages = true;
                }});
                
                // Hide pagination during search
                document.getElementById('messagePagination').style.display = 'none';
                
                // Show no results message
                document.getElementById('noResultsMessage').style.display = hasVisibleMessages ? 'none' : 'block';
            }} else {{
                // Reset to pagination view
                document.getElementById('noResultsMessage').style.display = 'none';
                document.getElementById('messagePagination').style.display = 'flex';
                showPage(1);
            }}
        }}
        
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
            
            // Initialize charts if needed
            if (tabId === 'chart-tab' && !window.chartsInitialized) {{
                initializeCharts();
                window.chartsInitialized = true;
            }}
        }}
        
        function initializeCharts() {{
            // Message distribution chart (time of day)
            const messagesByHour = Array(24).fill(0);
            document.querySelectorAll('.message').forEach(message => {{
                const dateStr = message.querySelector('.date').textContent;
                if (dateStr && dateStr !== 'Unknown date') {{
                    try {{
                        const date = new Date(dateStr);
                        const hour = date.getHours();
                        messagesByHour[hour]++;
                    }} catch (e) {{
                        // Skip invalid dates
                    }}
                }}
            }});
            
            const ctx2 = document.getElementById('timeDistributionChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: Array.from({{length: 24}}, (_, i) => `${{i}}:00`),
                    datasets: [{{
                        label: 'Messages by Hour',
                        data: messagesByHour,
                        borderColor: 'rgba(74, 105, 189, 1)',
                        backgroundColor: 'rgba(74, 105, 189, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}
        
        let currentPage = 1;
        window.onload = function() {{
            // Initialize with first tab
            showTab('messages-tab');
            
            // Initialize messages pagination
            showPage(1);
            
            // Initialize show all button
            document.getElementById('showAllBtn').addEventListener('click', function() {{
                document.getElementById('messageSearch').value = '';
                filterMessages();
            }});
        }};
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 Group Messages Report</h1>
            <h2>{group.title}</h2>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(messages)}</div>
                <div>Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(top_users)}</div>
                <div>Active Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for m in messages if m['has_media'])}</div>
                <div>Messages with Media</div>
            </div>
        </div>
        
        <div class="tab-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="messages-tab" onclick="showTab('messages-tab')">Messages</button>
                <button class="tab-button" data-tab="users-tab" onclick="showTab('users-tab')">Top Users</button>
                <button class="tab-button" data-tab="chart-tab" onclick="showTab('chart-tab')">Charts</button>
            </div>
            
            <div id="messages-tab" class="tab-content">
                <h2>💬 Messages</h2>
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <input type="text" id="messageSearch" class="search-box" placeholder="Search messages..." onkeyup="filterMessages()" style="flex: 1;">
                    <button id="showAllBtn" style="padding: 10px; background: #4a69bd; color: white; border: none; border-radius: 5px; cursor: pointer;">Show All</button>
                </div>
                <div id="noResultsMessage" style="display: none; text-align: center; padding: 20px; background: #f8d7da; color: #721c24; border-radius: 5px;">
                    No messages found matching your search.
                </div>
        """
        
        # Show messages (initially just the first page)
        # Sort messages by date (newest first)
        sorted_messages = sorted(messages, key=lambda x: x['date'] or '', reverse=True)
        
        for msg in sorted_messages[:100]:  # Limit to 100 most recent messages
            date_str = msg['date'][:16] if msg['date'] else 'Unknown date'
            
            html_content += f"""
            <div class="message">
                <div class="message-header">
                    <span>User ID: {msg['sender_id']}</span>
                    <span class="date">{date_str}</span>
                </div>
                <div class="message-text">{msg['text'] or 'No text content'}</div>
            </div>
            """
        
        html_content += """
                <div id="messagePagination" class="pagination"></div>
            </div>
            
            <div id="users-tab" class="tab-content">
                <h2>📊 Top Users</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Username</th>
                            <th>Messages Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        total_messages = len(messages)
        for i, user in enumerate(top_users[:20], 1):  # Top 20 users
            user_info = user['user_info']
            username = user_info.get('username', 'unknown') or f"{user_info.get('first_name', '')} (ID: {user['user_id']})"
            percentage = (user['count'] / total_messages) * 100 if total_messages else 0
            
            html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td>@{username}</td>
                            <td>{user['count']}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div id="chart-tab" class="tab-content">
                <h2>📈 Data Visualization</h2>
                
                <div class="chart-container">
                    <h3>Message Distribution by Time of Day</h3>
                    <canvas id="timeDistributionChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
