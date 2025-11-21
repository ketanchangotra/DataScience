"""
Output formatting utilities
"""

import pandas as pd
from tabulate import tabulate
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

def format_dataframe_for_display(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Format dataframe for terminal display
    
    Args:
        df: Dataframe to format
        max_rows: Maximum rows to display
    
    Returns:
        Formatted string
    """
    if df.empty:
        return Fore.YELLOW + "No results found."
    
    # Limit rows
    display_df = df.head(max_rows)
    
    # Format table
    table = tabulate(
        display_df,
        headers='keys',
        tablefmt='fancy_grid',
        showindex=False,
        numalign='right',
        stralign='left'
    )
    
    # Add summary
    summary = f"\n{Fore.CYAN}Showing {len(display_df)} of {len(df)} total records"
    
    return table + summary

def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"{Fore.CYAN}ℹ {message}")

def print_section_header(title: str):
    """Print section header"""
    width = 60
    print(f"\n{Fore.BLUE}{'='*width}")
    print(f"{Fore.BLUE}{title.center(width)}")
    print(f"{Fore.BLUE}{'='*width}\n")

def print_welcome_banner():
    """Print welcome banner"""
    banner = f"""{Fore.CYAN}
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        OTIF ALERT MANAGEMENT AI ASSISTANT                 ║
║        Multi-Agent System v1.0                            ║
║                                                            ║
║        Powered by AutoGen + GPT                           ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(banner)

def print_agent_message(agent_name: str, message: str):
    """Print message from agent"""
    colors = {
        "Orchestrator": Fore.MAGENTA,
        "QueryAgent": Fore.BLUE,
        "ActionSuggester": Fore.GREEN,
        "ExecutorAgent": Fore.YELLOW,
        "ReportGenerator": Fore.CYAN
    }
    
    color = colors.get(agent_name, Fore.WHITE)
    print(f"\n{color}[{agent_name}]{Style.RESET_ALL} {message}")
