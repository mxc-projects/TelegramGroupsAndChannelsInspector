#!/usr/bin/env python3
"""
Telegram Group Inspector - Main Application
"""

import asyncio
import logging
import os
import sys
from typing import Awaitable, Optional

from rich.console import Console
from rich.panel import Panel
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Ensure project root is on sys.path when running this file directly (python src/main.py)
if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

from src.config.config import config, logger
from src.config.connection_config import ConnectionConfig
from src.modules.group_scanner import GroupScanner
from src.modules.media_downloader import MediaDownloader
from src.modules.message_analyzer import MessageAnalyzer
from src.modules.user_scanner import UserScanner
from src.units.file_manager import FileSystemManager
from src.units.menu import OptimizedMenuSystem
from src.utils.async_processor import get_processor
from src.utils.console_manager import get_console


class OptimizedTelegramInspector:
    """Optimized Telegram Inspector with multithreading support"""

    def __init__(self):
        """Initialize the application with optimizations"""
        try:
            # Initialize console and processor
            self.console_manager = get_console()
            self.console = Console()
            self.processor = get_processor()

            # Initialize file system manager
            self.fs_manager = FileSystemManager()

            # API connection details
            self.api_id = config.api_id
            self.api_hash = config.api_hash
            self.phone = config.phone_number

            # Connection config
            self.conn_config = ConnectionConfig()

            # Create session path
            session_file = str(config.session_file)
            self._session_file = session_file
            self.client: Optional[TelegramClient] = None

            # Initialize optimized modules
            self.menu = OptimizedMenuSystem()
            self.group_scanner: Optional[GroupScanner] = None
            self.message_analyzer: Optional[MessageAnalyzer] = None
            self.media_downloader: Optional[MediaDownloader] = None
            self.user_scanner: Optional[UserScanner] = None

            logger.info("Optimized application initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize application: {e}")
            self.console.print(f"[bold red]Failed to initialize:[/] {e}")
            sys.exit(1)

    def _build_client(self) -> TelegramClient:
        """Create TelegramClient honoring connection config (proxy/tor/direct)."""
        api_id_int = (
            int(self.api_id) if not isinstance(self.api_id, int) else self.api_id
        )
        api_hash_str = str(self.api_hash)
        proxy = self.conn_config.get_proxy_tuple()
        if proxy:
            return TelegramClient(
                self._session_file, api_id_int, api_hash_str, proxy=proxy
            )
        return TelegramClient(self._session_file, api_id_int, api_hash_str)

    async def _test_connection(self) -> bool:
        """Attempt a short connection to validate proxy/tor settings before auth."""
        try:
            temp_client = self._build_client()
            await temp_client.connect()
            await temp_client.disconnect()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self.console.print(f"[bold red]Connection test failed:[/] {e}")
            return False

    async def connect(self):
        """Connect to Telegram API"""
        try:
            logger.info("Preparing to connect to Telegram...")
            self.console.print("[yellow]Preparing to connect to Telegram...[/]")

            # If proxy/tor selected, verify connectivity first
            if self.conn_config.is_proxy_mode():
                self.console.print("[cyan]Testing proxy/Tor connectivity...[/]")
                ok = await self._test_connection()
                if not ok:
                    self.console.print(
                        "[bold red]Proxy/Tor connectivity failed. Adjust settings in Connection Config.[/]"
                    )
                    return False

            # Build real client and connect
            self.client = self._build_client()
            await self.client.connect()

            # Check authorization
            if not await self.client.is_user_authorized():
                logger.info("Not authorized, sending code request...")
                self.console.print("[yellow]Not authorized, sending code request...[/]")
                await self.client.send_code_request(self.phone)

                code = self.menu.input_with_prompt(
                    "Enter the authentication code you received"
                )
                try:
                    await self.client.sign_in(self.phone, code)
                except SessionPasswordNeededError:
                    password = self.menu.input_with_prompt(
                        "Two-step verification enabled. Please enter your password"
                    )
                    await self.client.sign_in(password=password)

            # Initialize modules that require active client
            self.group_scanner = GroupScanner(self.client)
            self.message_analyzer = MessageAnalyzer(self.client)
            self.media_downloader = MediaDownloader(self.client, self.fs_manager)
            self.user_scanner = UserScanner(self.client)

            logger.info("Successfully connected to Telegram")
            self.console.print("[bold green]✓[/] Successfully connected to Telegram")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.console.print(f"[bold red]Failed to connect:[/] {e}")
            return False

    async def _disconnect_client(self):
        """Robust disconnect to satisfy different stubs and runtimes"""
        try:
            if self.client:
                await self.client.disconnect()  # type: ignore[misc]
        except TypeError:
            if self.client:
                maybe_awaitable = self.client.disconnect()
                if isinstance(maybe_awaitable, Awaitable):
                    await maybe_awaitable

    async def run(self):
        """Optimized main application loop"""
        try:
            while True:
                # Show main menu and get target type selection
                target_type = await self.menu.show_main_menu_choice()

                if target_type == "config":
                    # Configure connection before connecting
                    ok = self.menu.show_connection_config(self.conn_config)
                    if ok:
                        self.console_manager.show_status(
                            "Connection settings updated", "success"
                        )
                    self.menu.wait_for_enter()
                    continue

                # Connect lazily only when user wants to perform actions
                if not self.client:
                    connected = await self.connect()
                    if not connected:
                        self.menu.wait_for_enter()
                        continue

                if target_type == "group":
                    await self.handle_group_target()
                elif target_type == "user":
                    await self.handle_user_target()
                else:
                    logger.info("Exiting application")
                    self.console_manager.show_status(
                        "Thank you for using Telegram Inspector!", "success"
                    )
                    break
        except KeyboardInterrupt:
            logger.info("Application terminated by user")
            self.console_manager.show_status(
                "Application terminated by user", "warning"
            )
        finally:
            await self._disconnect_client()
            self.processor.shutdown()
            logger.info("Disconnected from Telegram")

    async def handle_group_target(self):
        """Handle group/channel target selection and actions"""
        assert self.client is not None
        self.menu.clear_screen()
        self.console.print("[bold blue]Fetching your groups and channels...[/]")

        # Get groups and channels
        groups = []
        channels = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog)
            elif dialog.is_channel and not (
                hasattr(dialog.entity, "megagroup") and dialog.entity.megagroup
            ):
                channels.append(dialog)
            elif (
                dialog.is_channel
                and hasattr(dialog.entity, "megagroup")
                and dialog.entity.megagroup
            ):
                # This is actually a supergroup, but Telegram API treats it as a channel
                groups.append(dialog)

        dialogs = groups + channels

        if not dialogs:
            self.menu.display_warning(
                "No groups or channels found. Please join some groups or channels first."
            )
            self.menu.press_enter_to_continue()
            return

        # Show group selection menu
        selected_dialog = await self.menu.show_group_selection(groups, channels)

        if not selected_dialog:
            logger.info("No group selected, returning to main menu")
            return

        # For channels, show channel-specific options
        if selected_dialog.is_channel and not (
            hasattr(selected_dialog.entity, "megagroup")
            and selected_dialog.entity.megagroup
        ):
            # Ensure modules are initialized
            assert self.message_analyzer is not None
            assert self.media_downloader is not None
            await self.handle_channel_target(selected_dialog)
            return
        else:
            # For groups, show group-specific options
            action = await self.menu.show_group_action_menu()

            if action == "analyze":
                assert self.message_analyzer is not None
                days_input = self.menu.input_with_prompt(
                    "Enter number of days back to analyze (default: all time)"
                )
                days_back = (
                    int(days_input)
                    if days_input.strip() and days_input.isdigit()
                    else None
                )

                result = await self.message_analyzer.analyze_group(
                    selected_dialog.entity, days_back=days_back
                )
                if result:
                    self.console.print(
                        f"[bold green]✓[/] Analysis complete! Results saved to: [cyan]{result['files']['html']}[/]"
                    )
                self.menu.press_enter_to_continue()
                return
            elif action == "bulk":
                # Analyze messages & bulk data: run analysis and media download
                assert self.message_analyzer is not None
                assert self.media_downloader is not None
                days_input = self.menu.input_with_prompt(
                    "Enter number of days back (default: all time)"
                )
                days_back = (
                    int(days_input)
                    if days_input.strip() and days_input.isdigit()
                    else None
                )

                analysis_result = await self.message_analyzer.analyze_group(
                    selected_dialog.entity, days_back=days_back
                )
                download_result = await self.media_downloader.download_group_media(
                    selected_dialog.entity, days_back=days_back
                )

                if analysis_result and download_result:
                    self.console.print(
                        Panel.fit(
                            f"[bold green]✓[/] Bulk operation complete!\n\n"
                            f"[bold]Analysis:[/] {analysis_result['files']['html']}\n"
                            f"[bold]Media downloaded:[/] {download_result['total_files']} files",
                            title="Bulk Complete",
                            border_style="green",
                        )
                    )
                self.menu.press_enter_to_continue()
                return
            elif action == "download":
                assert self.media_downloader is not None
                days_input = self.menu.input_with_prompt(
                    "Enter number of days back to download media (default: all time)"
                )
                days_back = (
                    int(days_input)
                    if days_input.strip() and days_input.isdigit()
                    else None
                )

                result = await self.media_downloader.download_group_media(
                    selected_dialog.entity, days_back=days_back
                )
                if result:
                    self.console.print(
                        f"[bold green]✓[/] Media download complete! [bold]{result['total_files']}[/] files downloaded."
                    )
                self.menu.press_enter_to_continue()
                return
            elif action == "list":
                # Just show the list again
                self.console.print("[cyan]Groups & Channels already listed above.[/]")
                self.menu.press_enter_to_continue()
                return
            elif action == "return":
                return

    async def handle_channel_target(self, channel):
        """Handle channel target with simplified options"""
        # Ensure modules are initialized
        assert self.message_analyzer is not None
        assert self.media_downloader is not None

        self.console.print(
            Panel.fit(
                f"Selected channel: [bold blue]{channel.name}[/]",
                title="Channel Analysis",
                border_style="blue",
            )
        )

        # Perform all actions for channel
        # Ask for days back once and use for both operations
        days_input = self.menu.input_with_prompt(
            "Enter number of days back to analyze (default: all time)"
        )
        days_back = (
            int(days_input) if days_input.strip() and days_input.isdigit() else None
        )

        analysis_result = await self.message_analyzer.analyze_channel(
            channel.entity, days_back=days_back
        )
        media_result = await self.media_downloader.download_channel_media(
            channel.entity, days_back=days_back
        )

        if analysis_result and media_result:
            self.console.print(
                Panel.fit(
                    f"[bold green]✓[/] Channel analysis complete!\n\n"
                    f"[bold]Analysis results:[/] {analysis_result['files']['html']}\n"
                    f"[bold]Media downloaded:[/] {media_result['total_files']} files\n"
                    f"[bold]Output directory:[/] {analysis_result['output_dir']}",
                    title="Analysis Complete",
                    border_style="green",
                )
            )

        self.menu.press_enter_to_continue()
        return

    async def handle_user_target(self):
        """Handle user target selection and actions"""
        # Ensure modules are initialized
        assert self.user_scanner is not None

        # Get user input
        user_input = self.menu.input_with_prompt(
            "\nEnter username, phone number, or user ID"
        )

        if not user_input:
            logger.warning("No user specified")
            self.console.print(
                "[bold yellow]No user specified. Returning to main menu.[/]"
            )
            self.menu.press_enter_to_continue()
            return

        # Ask for days back
        days_input = self.menu.input_with_prompt(
            "Enter number of days back to scan (default: all time)"
        )
        days_back = (
            int(days_input) if days_input.strip() and days_input.isdigit() else None
        )

        # Scan user
        result = await self.user_scanner.scan_user_across_groups(
            user_input, days_back=days_back
        )

        if result:
            self.console.print(
                Panel.fit(
                    f"[bold green]✓[/] User scan complete!\n\n"
                    f"[bold]Found:[/] {result['total_messages']} messages in {result['groups_count']} groups\n"
                    f"[bold]Results saved to:[/] {result['files']['html']}",
                    title="Scan Complete",
                    border_style="green",
                )
            )
        else:
            self.console.print(
                Panel.fit(
                    "[bold red]User scan failed. Please check the logs for details.[/]",
                    title="Scan Failed",
                    border_style="red",
                )
            )

        self.menu.press_enter_to_continue()
        return


async def main():
    """Application entry point"""
    # Create Rich console for prettier error display
    console = Console()

    # Configure logging to console for critical errors
    logging_console = logging.StreamHandler()
    logging_console.setLevel(logging.CRITICAL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logging_console.setFormatter(formatter)
    logger.addHandler(logging_console)

    try:
        # Create console manager for startup logo
        startup_console = get_console()

        # Display MXC-Projects logo and contact information
        startup_console.display_mxc_logo()

        # Wait for a few seconds to display the logo (3 seconds)
        await asyncio.sleep(3)

        # Create and run optimized application
        inspector = OptimizedTelegramInspector()
        await inspector.run()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        console.print(
            Panel.fit(
                f"[bold red]Application crashed:[/]\n{str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        Console().print(f"[bold red]Application crashed:[/] {e}")
        sys.exit(1)
