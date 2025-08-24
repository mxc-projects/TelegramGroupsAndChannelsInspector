#!/usr/bin/env python3
"""
Optimized Console Manager for Telegram Group Inspector
Enhanced visual controls with improved performance
"""

import os
import platform
import shutil
from typing import Optional

from rich.align import Align
from rich.box import DOUBLE, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.style import Style as RichStyle
from rich.table import Table
from rich.text import Text


class OptimizedConsoleManager:
    """Optimized console manager with performance improvements"""

    def __init__(self, width: Optional[int] = None):
        """Initialize console manager"""
        terminal_size = shutil.get_terminal_size()
        self.width = width or min(terminal_size.columns, 120)

        self.console = Console(
            width=self.width, force_terminal=True, color_system="auto"
        )

        # Optimized color scheme
        self.colors = {
            "primary": "bright_cyan",
            "secondary": "bright_blue",
            "success": "bright_green",
            "error": "bright_red",
            "warning": "bright_yellow",
            "accent": "bright_magenta",
            "text": "white",
            "muted": "dim white",
        }

    def clear_screen(self):
        """Clear screen efficiently"""
        self.console.clear()

    def display_mxc_logo(self):
        """Display optimized MXC-Projects logo"""
        logo = """
[bright_cyan]
███╗   ███╗██╗  ██╗ ██████╗      ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗███████╗
████╗ ████║╚██╗██╔╝██╔════╝      ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
██╔████╔██║ ╚███╔╝ ██║     █████╗██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   ███████╗
██║╚██╔╝██║ ██╔██╗ ██║     ╚════╝██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   ╚════██║
██║ ╚═╝ ██║██╔╝ ██╗╚██████╗      ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   ███████║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝
[/]"""

        contact_panel = Panel(
            """[bright_green]🚀 MXC-PROJECTS - Advanced Software Solutions[/]

[bright_white]📱 Telegram:[/] [bright_cyan]@hoxedzik666[/]
[bright_white]🌐 Web:[/] [bright_cyan]mxc-projects.com[/]
[bright_white]💼 Focus:[/] [bright_yellow]Telegram Tools & Automation[/]
[bright_white]🔧 Project:[/] [bright_magenta]Telegram Groups Inspector v2.0[/]

[dim]Thanks for using our software! Contact us for custom development.[/]""",
            title="[bold bright_green]Contact Information[/]",
            border_style="bright_green",
            expand=False,
        )

        self.console.print(Align.center(logo))
        self.console.print()
        self.console.print(Align.center(contact_panel))
        self.console.print()

        separator = "━" * (self.width - 10)
        self.console.print(f"[bright_yellow]{separator}[/]")
        self.console.print("[bright_magenta]🚀 Initializing system...[/]")

    def create_header_panel(self, title: str, subtitle: str = "") -> Panel:
        """Create optimized header panel"""
        content = f"[bold {self.colors['primary']}]{title}[/]"
        if subtitle:
            content += f"\n[{self.colors['muted']}]{subtitle}[/]"

        return Panel(
            Align.center(content),
            box=DOUBLE,
            border_style=self.colors["primary"],
            expand=False,
            width=self.width - 10,
        )

    def display_menu_section(self, title: str, options: list):
        """Display optimized menu section"""
        # Header
        header = f"[bold {self.colors['secondary']}]📋 {title}[/]"
        self.console.print(header)

        separator = "─" * (len(title) + 4)
        self.console.print(f"[{self.colors['secondary']}]{separator}[/]")
        self.console.print()

        # Options
        for option in options:
            if isinstance(option, dict):
                num = option.get("number", "")
                desc = option.get("description", "")
                extra = option.get("extra_info", "")

                option_line = f"  [bold {self.colors['accent']}]{num}.[/] [{self.colors['text']}]{desc}[/]"
                if extra:
                    option_line += f" [{self.colors['muted']}]({extra})[/]"

                self.console.print(option_line)
            else:
                self.console.print(f"  {option}")

        self.console.print()
        separator = "═" * (self.width - 20)
        self.console.print(f"[{self.colors['primary']}]{separator}[/]")

    def create_table(self, title: str, columns: list, data: list) -> Table:
        """Create optimized table"""
        table = Table(
            title=f"[bold {self.colors['primary']}]{title}[/]",
            box=ROUNDED,
            border_style=self.colors["secondary"],
            header_style=f"bold {self.colors['secondary']}",
            show_header=True,
            highlight=True,
            expand=False,
        )

        for col in columns:
            if isinstance(col, dict):
                table.add_column(
                    col.get("header", ""),
                    style=col.get("style", self.colors["text"]),
                    justify=col.get("justify", "left"),
                    width=col.get("width"),
                )
            else:
                table.add_column(str(col), style=self.colors["text"])

        for row in data:
            if isinstance(row, (list, tuple)):
                table.add_row(*[str(cell) for cell in row])

        return table

    def get_input(self, prompt: str) -> str:
        """Get user input with styled prompt"""
        self.console.print()
        prompt_text = f"[bold {self.colors['accent']}]❯ {prompt}:[/] "
        self.console.print(prompt_text, end="")
        return input()

    def show_status(self, message: str, status: str = "info"):
        """Show status message"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳",
        }

        color = self.colors.get(status, self.colors["text"])
        icon = icons.get(status, "ℹ️")

        self.console.print(f"[{color}]{icon} {message}[/]")

    def create_progress_bar(self, description: str = "Processing..."):
        """Create progress bar for long operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )

    def wait_for_enter(self, message: str = "Press Enter to continue"):
        """Wait for user input"""
        self.console.print()
        self.console.print(f"[dim]⏸️ {message}...[/]", end="")
        input()


# Global instance
_console_manager: Optional[OptimizedConsoleManager] = None


def get_console() -> OptimizedConsoleManager:
    """Get global console manager instance"""
    global _console_manager
    if _console_manager is None:
        _console_manager = OptimizedConsoleManager()
    return _console_manager

    def clear_screen(self):
        """Clear the terminal screen with enhanced clearing"""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        # Reset cursor position
        self.console.print("\033[H", end="")

    def set_terminal_title(self, title: str):
        """Set terminal window title"""
        if platform.system() == "Windows":
            os.system(f"title {title}")
        else:
            print(f"\033]0;{title}\007", end="")

    def print_large_header(self, title: str, subtitle: str = ""):
        """Print a large, prominent header with enhanced styling"""
        self.clear_screen()
        self.set_terminal_title(f"Telegram Inspector - {title}")

        # Create title panel with enhanced styling
        title_text = Text(title, style=self.colors["title"])
        title_text.stylize("bold")

        if subtitle:
            subtitle_text = Text(f"\n{subtitle}", style=self.colors["info"])
            title_text.append(subtitle_text)

        panel = Panel(
            Align.center(title_text),
            box=DOUBLE,
            border_style="bright_cyan",
            padding=(1, 2),
            width=self.width - 10,
            expand=False,
        )

        self.console.print()
        self.console.print(Align.center(panel))
        self.console.print()

    def print_section_separator(self, style: str = "main"):
        """Print a section separator with enhanced styling"""
        separator = self.separators.get(style, self.separators["main"])
        self.console.print(f"[{self.colors['separator']}]{separator}[/]")

    def print_menu_option(self, number: str, description: str, extra_info: str = ""):
        """Print a menu option with enhanced formatting"""
        option_text = f"[{self.colors['option']}]{number}.[/]"
        desc_text = f"[{self.colors['description']}]{description}[/]"

        if extra_info:
            extra_text = f"[{self.colors['info']}] ({extra_info})[/]"
            line = f"  {option_text} {desc_text}{extra_text}"
        else:
            line = f"  {option_text} {desc_text}"

        self.console.print(line)

    def print_menu_section(
        self, title: str, options: list, show_separators: bool = True
    ):
        """Print a complete menu section with enhanced styling"""
        if show_separators:
            self.print_section_separator("sub")

        self.console.print()
        self.console.print(f"[{self.colors['header']}]📋 {title}:[/]")
        self.console.print()

        for option in options:
            if isinstance(option, dict):
                self.print_menu_option(
                    option.get("number", ""),
                    option.get("description", ""),
                    option.get("extra_info", ""),
                )
            elif isinstance(option, tuple) and len(option) >= 2:
                self.print_menu_option(
                    option[0], option[1], option[2] if len(option) > 2 else ""
                )
            else:
                self.console.print(f"  {option}")

        self.console.print()
        if show_separators:
            self.print_section_separator("sub")

    def create_enhanced_table(
        self,
        title: str,
        columns: list,
        data: list,
        highlight_rows: bool = True,
        show_lines: bool = True,
    ) -> Table:
        """Create an enhanced table with better styling"""

        table = Table(
            title=title,
            title_style=self.colors["title"],
            box=ROUNDED if show_lines else None,
            border_style="bright_blue",
            header_style=self.colors["header"],
            show_header=True,
            highlight=highlight_rows,
            show_lines=show_lines,
            width=self.width - 10,
            expand=False,
        )

        # Add columns
        for col in columns:
            if isinstance(col, dict):
                table.add_column(
                    col.get("header", ""),
                    style=col.get("style", "white"),
                    justify=col.get("justify", "left"),
                    width=col.get("width"),
                    no_wrap=col.get("no_wrap", True),
                )
            else:
                table.add_column(str(col), style="white")

        # Add data rows
        for row in data:
            if isinstance(row, (list, tuple)):
                table.add_row(*[str(cell) for cell in row])
            else:
                table.add_row(str(row))

        return table

    def display_enhanced_table(self, title: str, columns: list, data: list, **kwargs):
        """Display an enhanced table with spacing"""
        table = self.create_enhanced_table(title, columns, data, **kwargs)

        self.console.print()
        self.console.print(Align.center(table))
        self.console.print()

    def input_with_enhanced_prompt(self, prompt: str, style: str = "prompt") -> str:
        """Get user input with enhanced styling"""
        self.console.print()
        self.print_section_separator("dots")
        prompt_style = self.colors.get(style, self.colors["prompt"])
        self.console.print(f"[{prompt_style}]➤ {prompt}:[/]", end=" ")
        return input()

    def display_status_message(self, message: str, status_type: str = "info"):
        """Display a status message with enhanced styling"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳",
            "completed": "✨",
        }

        icon = icons.get(status_type, "ℹ️")
        style = self.colors.get(status_type, self.colors["info"])

        self.console.print(f"[{style}]{icon} {message}[/]")

    def display_progress_indicator(self, message: str):
        """Display a simple progress indicator"""
        self.console.print(f"[{self.colors['info']}]⏳ {message}...[/]")

    def press_enter_to_continue(self, message: str = "Press Enter to continue"):
        """Enhanced press enter prompt"""
        self.console.print()
        self.print_section_separator("dots")
        self.console.print(f"[{self.colors['prompt']}]⏸️  {message}...[/]", end="")
        input()

    def display_mxc_logo_and_contact(self):
        """Display MXC-Projects logo and contact information"""
        # Clear screen first
        self.clear_screen()

        # MXC-Projects logo made with special characters
        logo = """
███╗   ███╗██╗  ██╗ ██████╗      ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗███████╗
████╗ ████║╚██╗██╔╝██╔════╝      ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
██╔████╔██║ ╚███╔╝ ██║     █████╗██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   ███████╗
██║╚██╔╝██║ ██╔██╗ ██║     ╚════╝██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   ╚════██║
██║ ╚═╝ ██║██╔╝ ██╗╚██████╗      ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   ███████║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝
        """

        # Alternative ASCII logo using # and other characters
        simple_logo = """
##     ## ##     ##  ######       ########  ########   #######          ## ########  ######  ########  ######  
###   ### ###   ### ##    ##      ##     ## ##     ## ##     ##         ## ##       ##    ##    ##    ##    ## 
#### #### #### #### ##            ##     ## ##     ## ##     ##         ## ##       ##          ##    ##       
## ### ## ## ### ## ##            ########  ########  ##     ##         ## ######   ##          ##     ######  
##     ## ##     ## ##            ##        ##   ##   ##     ##    ##   ## ##       ##          ##          ## 
##     ## ##     ## ##    ##      ##        ##    ##  ##     ##    ##   ## ##       ##    ##    ##    ##    ## 
##     ## ##     ##  ######       ##        ##     ##  #######      #####  ########  ######     ##     ######  
        """

        # Contact and project information
        contact_info = """
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    MXC-PROJECTS                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                               ║
║  📱 Telegram: @hoxedzik666                                                                    ║
║  🌐 Web: mxc-projects.com                                                                     ║
║  💼 Specialized in: Telegram Tools, Automation, Security Solutions                           ║
║  🔧 Current Project: Telegram Groups Inspector v1.0                                          ║
║                                                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                                               ║
║  Thanks for using our software! For support and custom development,                          ║
║  contact us via Telegram. We create powerful tools for Telegram automation                   ║
║  and analysis.                                                                                ║
║                                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
        """

        # Print the logo with colors
        self.console.print(f"[bold bright_cyan]{logo}[/]")
        self.console.print()

        # Print contact information
        self.console.print(f"[bold bright_green]{contact_info}[/]")
        self.console.print()

        # Add decorative separator
        separator = "━" * (self.width - 10)
        self.console.print(f"[bold bright_yellow]{separator}[/]")
        self.console.print()

        # Loading message
        self.console.print(
            "[bold bright_magenta]🚀 Initializing Telegram Groups Inspector...[/]"
        )
        self.console.print(
            "[bright_white]Please wait while we prepare the application for you...[/]"
        )
        self.console.print()

    def display_welcome_banner(self):
        """Display a welcome banner with ASCII art"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      TELEGRAM GROUPS INSPECTOR                               ║
║         Advanced Analysis Tool ----- Made by @hoxed666                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """

        self.console.print(f"[{self.colors['title']}]{banner}[/]")

    def create_info_panel(
        self, title: str, content: str, panel_style: str = "info"
    ) -> Panel:
        """Create an information panel"""
        style_map = {
            "info": ("blue", "ℹ️"),
            "warning": ("yellow", "⚠️"),
            "error": ("red", "❌"),
            "success": ("green", "✅"),
        }

        border_style, icon = style_map.get(panel_style, ("blue", "ℹ️"))

        return Panel(
            f"{icon} {content}",
            title=f"[bold]{title}[/]",
            border_style=border_style,
            padding=(0, 1),
            expand=False,
        )

    def display_info_panel(self, title: str, content: str, panel_style: str = "info"):
        """Display an information panel"""
        panel = self.create_info_panel(title, content, panel_style)
        self.console.print()
        self.console.print(panel)
        self.console.print()

    def get_console_dimensions(self) -> tuple:
        """Get current console dimensions"""
        return (self.width, self.height)

    def set_console_size(self, width: int, height: int):
        """Update console dimensions"""
        self.width = width
        self.height = height
        self.console = Console(width=width, force_terminal=True)

        # Update separators
        for key in self.separators:
            char = self.separators[key][0]
            self.separators[key] = char * (width - 20)
        self.console = Console(width=width, force_terminal=True)

        # Update separators
        for key in self.separators:
            char = self.separators[key][0]
            self.separators[key] = char * (width - 20)
