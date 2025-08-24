#!/usr/bin/env python3
"""
Optimized Menu System for Telegram Group Inspector
Enhanced aesthetics with improved performance
"""

from rich.console import Console
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.console_manager import get_console


class OptimizedMenuSystem:
    """Optimized menu interface with enhanced aesthetics"""

    def __init__(self):
        """Initialize optimized menu system"""
        self.console_manager = get_console()
        self.console = self.console_manager.console

    def clear_screen(self):
        """Clear screen"""
        self.console_manager.clear_screen()

    def display_main_menu(self):
        """Display main menu with enhanced aesthetics"""
        header = self.console_manager.create_header_panel(
            "TELEGRAM GROUP INSPECTOR",
            "Advanced Analysis Tool - MXC Projects"
        )
        
        self.console.print()
        self.console.print(header)
        self.console.print()
        
        options = [
            {
                "number": "1", 
                "description": "🔍 Groups & Channels", 
                "extra_info": "Analyze group activities"
            },
            {
                "number": "2", 
                "description": "👤 Individual User", 
                "extra_info": "Scan specific user"
            },
            {
                "number": "3", 
                "description": "⚙️ Connection Config", 
                "extra_info": "Proxy & network settings"
            }
        ]
        
        self.console_manager.display_menu_section("Select Target Type", options)
        
        exit_option = [{"number": "0", "description": "🚪 Exit", "extra_info": "Close application"}]
        self.console_manager.display_menu_section("Navigation", exit_option)

    def display_group_menu(self):
        """Display group actions menu"""
        header = self.console_manager.create_header_panel(
            "GROUPS & CHANNELS",
            "Choose your analysis method"
        )
        
        self.console.print()
        self.console.print(header)
        self.console.print()
        
        options = [
            {
                "number": "1", 
                "description": "📋 List Groups & Channels", 
                "extra_info": "Browse available groups"
            },
            {
                "number": "2", 
                "description": "📊 Analyze Messages", 
                "extra_info": "Message analysis & stats"
            },
            {
                "number": "3", 
                "description": "📦 Bulk Analysis", 
                "extra_info": "Messages + media download"
            },
            {
                "number": "4", 
                "description": "💾 Download Media", 
                "extra_info": "Extract all media files"
            }
        ]
        
        self.console_manager.display_menu_section("Available Actions", options)
        
        nav_options = [{"number": "5", "description": "🔙 Back", "extra_info": "Return to main menu"}]
        self.console_manager.display_menu_section("Navigation", nav_options)

    def display_user_menu(self):
        """Display user actions menu"""
        header = self.console_manager.create_header_panel(
            "USER ANALYSIS",
            "Scan individual users across groups"
        )
        
        self.console.print()
        self.console.print(header)
        self.console.print()
        
        options = [
            {
                "number": "1", 
                "description": "🔍 Scan User Activities", 
                "extra_info": "Comprehensive user analysis"
            }
        ]
        
        self.console_manager.display_menu_section("Available Actions", options)
        
        nav_options = [{"number": "2", "description": "🔙 Back", "extra_info": "Return to main menu"}]
        self.console_manager.display_menu_section("Navigation", nav_options)

    def display_groups_table(self, groups, channels):
        """Display groups and channels in optimized table"""
        columns = [
            {"header": "#", "style": "bright_cyan", "justify": "center", "width": 4},
            {"header": "ID", "style": "white", "justify": "right", "width": 12},
            {"header": "Name", "style": "bright_white", "justify": "left", "width": 35},
            {"header": "Type", "style": "bright_green", "justify": "center", "width": 15},
            {"header": "Members", "style": "bright_magenta", "justify": "right", "width": 10}
        ]
        
        all_dialogs = []
        data = []
        counter = 1

        # Process groups
        for dialog in groups:
            group_type = "Group"
            if hasattr(dialog.entity, "megagroup") and dialog.entity.megagroup:
                group_type = "Supergroup"
            elif hasattr(dialog.entity, "gigagroup") and dialog.entity.gigagroup:
                group_type = "Broadcast"

            data.append([
                str(counter),
                str(dialog.id),
                dialog.name[:35],
                f"[green]{group_type}[/]",
                str(getattr(dialog.entity, "participants_count", "N/A"))
            ])
            all_dialogs.append(dialog)
            counter += 1

        # Process channels
        for dialog in channels:
            data.append([
                str(counter),
                str(dialog.id),
                dialog.name[:35],
                "[blue]Channel[/]",
                str(getattr(dialog.entity, "participants_count", "N/A"))
            ])
            all_dialogs.append(dialog)
            counter += 1

        if data:
            table = self.console_manager.create_table(
                "Available Groups and Channels", 
                columns, 
                data
            )
            self.console.print()
            self.console.print(table)
            self.console.print()

        return all_dialogs

    def show_connection_config(self, conn_config):
        """Display connection configuration menu"""
        header = self.console_manager.create_header_panel(
            "CONNECTION SETUP",
            "Configure proxy and network settings"
        )
        
        self.console.print()
        self.console.print(header)
        self.console.print()
        
        options = [
            {"number": "1", "description": "🌐 Direct Connection", "extra_info": "No proxy"},
            {"number": "2", "description": "🔒 Tor Network", "extra_info": "SOCKS5 127.0.0.1:9050"},
            {"number": "3", "description": "🛡️ Custom Proxy", "extra_info": "Configure custom proxy"}
        ]
        
        self.console_manager.display_menu_section("Connection Methods", options)
        
        choice = self.get_input("Enter your choice")

        if choice == "1":
            conn_config.set_mode("direct")
        elif choice == "2":
            conn_config.set_tor_defaults()
        elif choice == "3":
            proxy_type = self.get_input("Proxy type (socks5/socks4/http)").lower() or "socks5"
            host = self.get_input("Proxy host (default 127.0.0.1)") or "127.0.0.1"
            port_str = self.get_input("Proxy port (e.g. 1080)") or "1080"
            user = self.get_input("Username (optional)") or None
            pwd = self.get_input("Password (optional)") or None
            
            try:
                conn_config.set_mode("proxy")
                conn_config.set_proxy(proxy_type, host, int(port_str), user, pwd)
            except Exception:
                self.show_status("Invalid proxy settings", "error")
                return False
        else:
            self.show_status("Invalid choice", "error")
            return False

        conn_config.save()
        self.show_status("Connection settings saved successfully", "success")
        return True

    async def show_main_menu_choice(self):
        """Show main menu and get user choice"""
        self.display_main_menu()
        
        while True:
            choice = self.get_input("Enter your choice")
            
            if choice in ["1", "2", "3", "0"]:
                return {"1": "group", "2": "user", "3": "config", "0": "exit"}[choice]
            else:
                self.show_status("Invalid choice. Please try again", "error")

    async def show_group_selection(self, groups, channels):
        """Show group selection interface"""
        self.clear_screen()
        all_dialogs = self.display_groups_table(groups, channels)

        if not all_dialogs:
            self.show_status("No groups or channels found", "warning")
            return None

        while True:
            choice = self.get_input(f"Select group/channel (1-{len(all_dialogs)}) or '0' to cancel")

            if choice == "0":
                return None

            try:
                index = int(choice) - 1
                if 0 <= index < len(all_dialogs):
                    return all_dialogs[index]
                else:
                    self.show_status("Invalid selection. Please try again", "error")
            except ValueError:
                self.show_status("Please enter a valid number", "error")

    async def show_group_action_menu(self):
        """Show group action menu and get choice"""
        self.display_group_menu()

        while True:
            choice = self.get_input("Enter your choice")

            actions = {
                "1": "list", "2": "analyze", "3": "bulk", 
                "4": "download", "5": "return"
            }
            
            if choice in actions:
                return actions[choice]
            else:
                self.show_status("Invalid choice. Please try again", "error")

    def get_input(self, prompt: str) -> str:
        """Get user input"""
        return self.console_manager.get_input(prompt)

    def show_status(self, message: str, status: str = "info"):
        """Show status message"""
        self.console_manager.show_status(message, status)

    def wait_for_enter(self, message: str = "Press Enter to continue"):
        """Wait for user input"""
        self.console_manager.wait_for_enter(message)

    # Compatibility methods for existing code
    def display_success(self, message: str):
        """Display success message"""
        self.show_status(message, "success")

    def display_error(self, message: str):
        """Display error message"""
        self.show_status(message, "error")

    def display_warning(self, message: str):
        """Display warning message"""
        self.show_status(message, "warning")

    def display_info(self, message: str):
        """Display info message"""
        self.show_status(message, "info")

    def input_with_prompt(self, prompt: str):
        """Get input with prompt (compatibility)"""
        return self.get_input(prompt)

    def press_enter_to_continue(self):
        """Press enter to continue (compatibility)"""
        self.wait_for_enter()

    def display_groups_and_channels_table(self, groups, channels):
        """Compatibility method"""
        return self.display_groups_table(groups, channels)

    async def show_main_menu(self):
        """Compatibility method"""
        return await self.show_main_menu_choice()


# Alias for backward compatibility
MenuSystem = OptimizedMenuSystem
