#!/usr/bin/env python3
"""
Message Analyzer Module for Telegram Group Inspector
"""

import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

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

from ..config.config import config, logger
from ..units.file_manager import FileSystemManager

# Telethon imports for fetching full chat/channel info
try:
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.tl.functions.messages import GetFullChatRequest
except Exception:
    GetFullChannelRequest = None
    GetFullChatRequest = None


class MessageAnalyzer:
    """Analyzes messages from Telegram groups and channels"""

    def __init__(self, client):
        """Initialize the message analyzer"""
        self.client = client
        self.fs_manager = FileSystemManager()
        self.message_limit = config.default_message_limit
        self.console = Console()

    async def analyze_group(self, entity, days_back=None):
        """Analyze messages in a group"""
        logger.info(f"Analyzing group: {entity.title}")
        self.console.print(
            Panel(
                f"[bold cyan]Analyzing messages in group: [/][bold white]{entity.title}[/]",
                border_style="blue",
            )
        )

        # Get days back from user if not provided
        if days_back is None:
            days_input = input(
                "Enter number of days back to analyze (default: all messages): "
            )
            if days_input.strip() and days_input.isdigit():
                days_back = int(days_input)
                self.console.print(
                    f"[green]Analyzing messages from the last {days_back} days...[/]"
                )
            else:
                days_back = 0
                self.console.print("[green]Analyzing all available messages...[/]")

        # Calculate date limit if days_back is specified
        date_limit = None
        if days_back > 0:
            date_limit = datetime.now() - timedelta(days=days_back)
            logger.info(f"Setting date limit to: {date_limit}")

        self.console.print(
            "[yellow]This may take some time depending on the message volume...[/]"
        )

        try:
            # Get messages
            messages = []
            users = {}
            user_message_count = Counter()

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold]{task.completed}[/] messages processed"),
                TimeElapsedColumn(),
                expand=True,
            ) as progress:
                analyze_task = progress.add_task(
                    "[cyan]Analyzing messages...", total=None
                )
                message_count = 0

                async for message in self.client.iter_messages(
                    entity, limit=self.message_limit
                ):
                    message_count += 1
                    progress.update(analyze_task, completed=message_count)

                    # Skip messages before date_limit if it's set
                    if (
                        date_limit
                        and message.date
                        and message.date.replace(tzinfo=None) < date_limit
                    ):
                        logger.info(
                            f"Reached date limit, stopping message collection at {message.date}"
                        )
                        break

                    if message.sender_id:
                        # Count messages per user
                        user_message_count[message.sender_id] += 1

                        # Get user info if not already stored
                        if message.sender_id not in users:
                            try:
                                user = await self.client.get_entity(message.sender_id)
                                users[message.sender_id] = {
                                    "id": user.id,
                                    "username": user.username,
                                    "first_name": (
                                        user.first_name
                                        if hasattr(user, "first_name")
                                        else None
                                    ),
                                    "last_name": (
                                        user.last_name
                                        if hasattr(user, "last_name")
                                        else None
                                    ),
                                    "phone": (
                                        user.phone if hasattr(user, "phone") else None
                                    ),
                                }
                            except Exception as e:
                                logger.warning(
                                    f"Could not get user info for {message.sender_id}: {e}"
                                )
                                users[message.sender_id] = {
                                    "id": message.sender_id,
                                    "username": "unknown",
                                    "first_name": "Unknown",
                                    "last_name": "User",
                                    "phone": None,
                                }

                    # Process message
                    msg_data = {
                        "id": message.id,
                        "date": message.date.isoformat() if message.date else None,
                        "sender_id": message.sender_id,
                        "text": message.text,
                        "has_media": message.media is not None,
                        "is_reply": message.reply_to is not None,
                        "forward": message.forward is not None,
                    }

                    messages.append(msg_data)

                # Update progress bar with final count
                progress.update(
                    analyze_task, total=message_count, completed=message_count
                )

            # Get top users
            top_users = user_message_count.most_common(20)
            top_users_data = [
                {
                    "user_id": uid,
                    "count": count,
                    "user_info": users.get(uid, {"id": uid}),
                }
                for uid, count in top_users
            ]

            # Show top users in a table
            self._display_top_users_table(top_users_data)

            # Prepare data for saving
            analysis_data = {
                "entity": {
                    "id": entity.id,
                    "title": entity.title,
                    "username": (
                        entity.username if hasattr(entity, "username") else None
                    ),
                },
                "analysis_date": datetime.now().isoformat(),
                "total_messages": len(messages),
                "total_users": len(users),
                "top_users": top_users_data,
                "messages": messages,
            }

            # Save data
            self.console.print("[cyan]Saving analysis results...[/]")
            json_path = self.fs_manager.save_json(
                analysis_data, entity, "analysis_data.json"
            )

            # Save list of most active users
            top_users_json = self.fs_manager.save_json(
                top_users_data, entity, "top_users.json"
            )

            # Generate HTML report
            html_report = self._generate_html_report(analysis_data)
            html_path = self.fs_manager.save_html(
                html_report, entity, "analysis_report.html"
            )

            # NEW: Save all active users (not only top)
            active_users_list = []
            for uid, info in users.items():
                active_users_list.append(
                    {
                        "user_id": uid,
                        "count": user_message_count.get(uid, 0),
                        "user_info": info,
                    }
                )
            # Sort by count desc
            active_users_list.sort(key=lambda u: u["count"], reverse=True)
            active_users_json = self.fs_manager.save_json(
                active_users_list, entity, "active_users.json"
            )

            # NEW: Extract links and save links.json
            links_entries = []
            link_pattern = re.compile(r"(https?://\S+)", re.IGNORECASE)
            for msg in messages:
                text = msg.get("text") or ""
                if not text:
                    continue
                found_links = link_pattern.findall(text)
                if not found_links:
                    continue
                sid = msg.get("sender_id")
                uinfo = users.get(sid, {})
                links_entries.append(
                    {
                        "first_name": uinfo.get("first_name"),
                        "last_name": uinfo.get("last_name"),
                        "username": uinfo.get("username"),
                        "user_id": uinfo.get("id", sid),
                        "message": text,
                        "links": found_links,
                        "message_id": msg.get("id"),
                        "date": msg.get("date"),
                    }
                )
            links_json = self.fs_manager.save_json(links_entries, entity, "links.json")

            # NEW: Build and save analyze_{group}.txt
            try:
                full_info = await self._fetch_entity_details(entity)
            except Exception as e:
                logger.warning(f"Could not fetch full entity details: {e}")
                full_info = {}

            analyze_txt_content = self._format_text_report(entity, analysis_data, full_info, active_users_list)
            out_dir = self.fs_manager.get_entity_output_dir(entity)
            safe_title = self._safe_filename(entity.title if hasattr(entity, 'title') else str(entity.id))
            analyze_filename = f"analyze_{safe_title}.txt"
            try:
                analyze_txt_path = self.fs_manager.save_text(analyze_txt_content, entity, analyze_filename)
            except AttributeError:
                analyze_txt_path = Path(out_dir) / analyze_filename
                analyze_txt_path.write_text(analyze_txt_content, encoding="utf-8")
                analyze_txt_path = str(analyze_txt_path)

            self.console.print(
                Panel(
                    f"[bold green]✅ Analysis complete![/]\n"
                    f"[cyan]Results saved to:[/] [white]{html_path}[/]",
                    border_style="green",
                )
            )

            return {
                'status': 'success',
                'output_dir': str(self.fs_manager.get_entity_output_dir(entity)),
                'files': {
                    'json': json_path,
                    'top_users': top_users_json,
                    'active_users': active_users_json,
                    'links': links_json,
                    'text_report': str(analyze_txt_path),
                    'html': html_path
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing group: {e}")
            self.console.print(f"[bold red]Error analyzing group: {e}[/]")
            return None

    def _display_top_users_table(self, top_users_data):
        """Display a table of top users"""
        table = Table(
            title="Top Active Users",
            title_style="bold cyan",
            box=ROUNDED,
            border_style="blue",
            header_style="bold cyan",
            show_header=True,
        )

        # Add columns
        table.add_column("Rank", style="cyan", justify="center", width=4)
        table.add_column("Username", style="white", width=25)
        table.add_column("User ID", style="white", width=15)
        table.add_column("Messages", style="green", justify="right", width=10)

        for i, user in enumerate(top_users_data, 1):
            user_info = user["user_info"]
            username = user_info.get("username", "N/A")
            first_name = user_info.get("first_name", "")
            last_name = user_info.get("last_name", "")

            display_name = (
                f"@{username}" if username else f"{first_name} {last_name}".strip()
            )
            if not display_name:
                display_name = f"User {user['user_id']}"

            table.add_row(
                str(i), display_name, str(user["user_id"]), str(user["count"])
            )

        self.console.print()
        self.console.print(table)

    async def analyze_channel(self, entity, days_back=None):
        """Analyze messages in a channel"""
        # For channels, we'll use the same analysis as for groups
        return await self.analyze_group(entity, days_back)

    def _generate_html_report(self, analysis_data):
        """Generate an HTML report from analysis data"""

        # Get basic info
        entity = analysis_data["entity"]
        total_messages = analysis_data["total_messages"]
        total_users = analysis_data["total_users"]
        top_users = analysis_data["top_users"]
        messages = analysis_data["messages"]

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Analysis: {entity['title']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .container {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4a69bd;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .highlight {{
            background-color: #ffeaa7;
        }}
        .user-rank {{
            font-weight: bold;
            text-align: center;
        }}
        .summary-item {{
            font-size: 1.2em;
            margin: 10px 0;
        }}
        .date {{
            color: #7f8c8d;
            font-style: italic;
        }}
        .message {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 5px solid #4a69bd;
        }}
        .message-date {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .message-sender {{
            font-weight: bold;
            color: #2980b9;
        }}
        .search-container {{
            margin-bottom: 20px;
        }}
        #searchInput {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .stat-box {{
            flex: 1;
            min-width: 200px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4a69bd;
        }}
    </style>
</head>
<body>
    <h1>Telegram Group Analysis: {entity['title']}</h1>
    <p class="date">Analysis generated on {analysis_data['analysis_date']}</p>
    
    <div class="container">
        <h2>📊 Summary</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{total_messages}</div>
                <div>Total Messages</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_users}</div>
                <div>Total Users</div>
            </div>
        </div>
        <div class="summary-item"><strong>Group/Channel:</strong> {entity['title']}</div>
        <div class="summary-item"><strong>Username:</strong> {entity['username'] if entity['username'] else 'N/A'}</div>
    </div>
    
    <div class="container">
        <h2>👥 Top Users by Message Count</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Username</th>
                <th>User ID</th>
                <th>Message Count</th>
                <th>% of Total</th>
            </tr>
        """

        # Add top users
        for i, user_data in enumerate(top_users, 1):
            user = user_data["user_info"]
            count = user_data["count"]
            percentage = (count / total_messages) * 100 if total_messages > 0 else 0

            username = user.get("username", "")
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")

            if username:
                display_name = f"@{username}"
            elif first_name or last_name:
                display_name = f"{first_name} {last_name}".strip()
            else:
                display_name = f"User {user_data['user_id']}"

            html += f"""
            <tr class="{'highlight' if i <= 3 else ''}">
                <td class="user-rank">{i}</td>
                <td>{display_name}</td>
                <td>{user_data['user_id']}</td>
                <td>{count}</td>
                <td>{percentage:.2f}%</td>
            </tr>"""

        html += """
        </table>
    </div>
    
    <div class="container">
        <h2>💬 Message Samples</h2>
        <div class="search-container">
            <input type="text" id="searchInput" onkeyup="filterMessages()" placeholder="Search messages...">
        </div>
        """

        # Add message samples
        for msg in messages[:100]:  # Limit to 100 messages for preview
            date_str = msg["date"][:16] if msg["date"] else "Unknown date"
            sender_id = msg["sender_id"] if msg["sender_id"] else "Unknown"

            # Get sender name if available
            sender_name = "Unknown"
            for user in top_users:
                if user["user_id"] == sender_id:
                    user_info = user["user_info"]
                    username = user_info.get("username")
                    first_name = user_info.get("first_name", "")
                    last_name = user_info.get("last_name", "")

                    if username:
                        sender_name = f"@{username}"
                    elif first_name or last_name:
                        sender_name = f"{first_name} {last_name}".strip()
                    break

            html += f"""
            <div class="message">
                <div class="message-sender">{sender_name} <span class="message-date">[{date_str}]</span></div>
                <div class="message-text">{msg['text'] or '(No text content)'}...</div>
            </div>
            """

        html += """
    </div>
    
    <div class="container">
        <h2>About This Report</h2>
        <p>This report was generated by Telegram Inspector Bot. It provides an analysis of message activity in the selected Telegram group or channel.</p>
        <p>Data is collected through the Telegram API using the Telethon library.</p>
        <p><strong>Note:</strong> This tool respects Telegram's API usage guidelines and only analyzes publicly available information.</p>
    </div>
    
    <script>
        function filterMessages() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const messages = document.getElementsByClassName('message');
            
            for (let i = 0; i < messages.length; i++) {
                const text = messages[i].textContent.toLowerCase();
                messages[i].style.display = text.includes(filter) ? 'block' : 'none';
            }
        }
    </script>
</body>
</html>
        """

        return html

    def _generate_channel_html_report(
        self, channel_entity, posts, html_file, channel_dir
    ):
        """Generate HTML report for channel content with media links"""
        # Sort posts by date (newest first)
        sorted_posts = sorted(posts, key=lambda x: x["date"] or "", reverse=True)

        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Channel Content Report - {channel_entity.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #dc3545; padding-bottom: 20px; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #dc3545; border-left: 4px solid #dc3545; padding-left: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #dc3545; }}
        .post {{ background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 20px 0; }}
        .post-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9em; color: #666; }}
        .post-date {{ color: #888; }}
        .post-text {{ line-height: 1.5; margin-bottom: 15px; }}
        .post-media {{ max-width: 100%; margin-top: 15px; }}
        .post-media img {{ max-width: 100%; border-radius: 5px; }}
        .post-media video {{ max-width: 100%; border-radius: 5px; }}
        .post-media audio {{ width: 100%; }}
        .search-box {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
    <script>
        function filterPosts() {{
            const input = document.getElementById('postSearch');
            const filter = input.value.toLowerCase();
            const posts = document.getElementsByClassName('post');
            
            for (let i = 0; i < posts.length; i++) {{
                const text = posts[i].textContent.toLowerCase();
                posts[i].style.display = text.includes(filter) ? 'block' : 'none';
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📺 Channel Content Report</h1>
            <h2>{channel_entity.title}</h2>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>📈 Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(posts)}</div>
                    <div>Total Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(1 for post in posts if post['has_media'])}</div>
                    <div>Posts with Media</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📝 Channel Posts</h2>
            <input type="text" id="postSearch" class="search-box" placeholder="Search posts..." onkeyup="filterPosts()">
        """

        for post in sorted_posts:
            date_str = post["date"][:16] if post["date"] else "Unknown date"
            media_path = post.get("media_path")
            media_type = post.get("media_type")

            html_content += f"""
            <div class="post">
                <div class="post-header">
                    <span class="post-id">Post #{post['id']}</span>
                    <span class="post-date">{date_str}</span>
                </div>
                <div class="post-text">{post['text'] or 'No text content'}</div>
            """

            # Add media if present
            if media_path:
                if media_type == "photo" or (
                    media_type == "document" and self._is_image_file(media_path)
                ):
                    html_content += f"""
                <div class="post-media">
                    <img src="{media_path}" alt="Post media" />
                </div>
                    """
                elif media_type == "video":
                    html_content += f"""
                <div class="post-media">
                    <video controls>
                        <source src="{media_path}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                    """
                elif media_type == "audio":
                    html_content += f"""
                <div class="post-media">
                    <audio controls>
                        <source src="{media_path}" type="audio/mpeg">
                        Your browser does not support the audio tag.
                    </audio>
                </div>
                    """
                else:
                    html_content += f"""
                <div class="post-media">
                    <p><a href="{media_path}" target="_blank">Download attached file</a></p>
                </div>
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
        if hasattr(media, "photo"):
            return "photo"
        elif hasattr(media, "document"):
            doc = media.document
            if hasattr(doc, "mime_type"):
                if doc.mime_type.startswith("image/"):
                    return "photo"
                elif doc.mime_type.startswith("video/"):
                    return "video"
                elif doc.mime_type.startswith("audio/"):
                    return "audio"
            return "document"
        else:
            return "document"

    def _get_mime_type(self, media):
        """Get mime type from media if available"""
        if hasattr(media, "document") and hasattr(media.document, "mime_type"):
            return media.document.mime_type
        return None

    def _get_file_extension(self, mime_type):
        """Get file extension from mime type"""
        if not mime_type:
            return ""

        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "video/mp4": ".mp4",
            "video/avi": ".avi",
            "audio/mpeg": ".mp3",
            "audio/ogg": ".ogg",
            "application/pdf": ".pdf",
        }

        return mime_to_ext.get(mime_type, "")

    def _is_image_file(self, file_path):
        """Check if file path has image extension"""
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        ext = Path(file_path).suffix.lower()
        return ext in image_extensions

    # NEW HELPERS

    async def _fetch_entity_details(self, entity):
        """Fetch extended details like description and members count."""
        details = {
            "status": None,
            "is_public": None,
            "has_username": None,
            "join_link": None,
            "description": None,
            "members_count": None,
        }

        try:
            title = getattr(entity, "title", "") or ""
            username = getattr(entity, "username", None)
            megagroup = getattr(entity, "megagroup", False)
            broadcast = getattr(entity, "broadcast", False)

            if megagroup:
                details["status"] = "supergroup"
            elif broadcast:
                details["status"] = "channel"
            else:
                details["status"] = "group"

            details["has_username"] = bool(username)
            details["is_public"] = bool(username)
            details["join_link"] = f"https://t.me/{username}" if username else None

            # Fetch full info
            if (
                GetFullChannelRequest
                and hasattr(entity, "id")
                and hasattr(entity, "megagroup")
                or broadcast
            ):
                try:
                    full = await self.client(GetFullChannelRequest(entity))
                    # ChannelFull fields vary across versions; guard with getattr
                    details["description"] = getattr(
                        full.full_chat, "about", None
                    ) or getattr(full, "about", None)
                    details["members_count"] = getattr(
                        full.full_chat, "participants_count", None
                    ) or getattr(full, "participants_count", None)
                except Exception:
                    pass

            # For basic chats
            if (
                details["members_count"] is None
                and GetFullChatRequest
                and getattr(entity, "id", None)
                and not broadcast
            ):
                try:
                    full = await self.client(GetFullChatRequest(entity.id))
                    details["description"] = details["description"] or getattr(
                        full.full_chat, "about", None
                    )
                    details["members_count"] = getattr(
                        full.full_chat, "participants_count", None
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"_fetch_entity_details fallback due to: {e}")

        return details

    def _safe_filename(self, name: str) -> str:
        """Create a safe filename from a title/name."""
        name = name.strip()
        # Replace spaces with underscores, remove disallowed characters
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^A-Za-z0-9._-]+", "", name)
        return name or "report"

    def _format_text_report(self, entity, analysis_data, full_info, ranked_users):
        """Format the requested analyze_{group}.txt content."""
        group_id = getattr(entity, "id", "N/A")
        group_name = getattr(entity, "title", "N/A")
        analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status = full_info.get("status") or "N/A"
        is_public = "True" if full_info.get("is_public") else "False"
        has_username = "True" if full_info.get("has_username") else "False"
        join_link = full_info.get("join_link") or "N/A"
        description = full_info.get("description") or ""
        members_count = full_info.get("members_count")
        total_members = members_count if members_count is not None else "N/A"

        active_users = len([u for u in ranked_users if u.get("count", 0) > 0])
        total_messages = analysis_data.get("total_messages", 0)

        # Build ranking lines (all active users)
        ranking_lines = []
        total_msgs = total_messages if total_messages else 1
        for i, u in enumerate(ranked_users, start=1):
            count = u.get("count", 0)
            if count <= 0:
                continue
            info = u.get("user_info", {})
            username = info.get("username")
            first_name = info.get("first_name") or ""
            last_name = info.get("last_name") or ""
            if username:
                display = f"@{username}"
            else:
                display = (
                    f"{first_name} {last_name}"
                ).strip() or f"User {u.get('user_id')}"
            percentage = (count / total_msgs) * 100
            ranking_lines.append(
                f"{i}. {display} (ID: {u.get('user_id')}) - {count} messages ({percentage:.2f}%)"
            )

        report = []
        report.append("TELEGRAM GROUP ACTIVITY ANALYSIS")
        report.append("==================================================")
        report.append("")
        report.append(f"Group ID: {group_id}")
        report.append(f"Group Name: {group_name}")
        report.append(f"Analysis Date: {analysis_date}")
        report.append("")
        report.append("GROUP INFORMATION:")
        report.append("------------------------------")
        report.append(f"Status: {status}")
        report.append(f"Is Public: {is_public}")
        report.append(f"Has Username: {has_username}")
        report.append(f"Join Link: {join_link}")
        report.append(f"Description: {description}")
        report.append(
            f"Members Count: {members_count if members_count is not None else 'N/A'}"
        )
        report.append("")
        report.append("STATISTICS:")
        report.append("------------------------------")
        report.append(f"Total Members: {total_members}")
        report.append(f"Active Users: {active_users}")
        report.append(f"Total Messages: {total_messages}")
        report.append("")
        report.append("USER ACTIVITY RANKING:")
        report.append("------------------------------")
        report.extend(ranking_lines)
        report.append("")

        return "\n".join(report)
