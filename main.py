"""
OTIF Alert Management Multi-Agent AI System
Main Application Entry Point
"""

import sys
import os
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from tools.data_loader import data_loader
from agents.orchestrator import create_orchestrator_agent
from agents.query_agent import create_query_agent
from agents.action_suggester import create_action_suggester_agent
from agents.executor_agent import create_executor_agent
from agents.report_generator import create_report_generator_agent
from memory.conversation_memory import conversation_memory
from utils.formatters import (
    print_welcome_banner, 
    print_success, 
    print_error, 
    print_info,
    print_section_header
)
import autogen

class OTIFAlertSystem:
    """Main OTIF Alert Management System"""
    
    def __init__(self):
        """Initialize the system"""
        self.initialized = False
        self.agents = {}
        self.user_proxy = None
        
    def initialize(self):
        """Initialize system components"""
        try:
            print_info("Initializing OTIF Alert Management System...")
            
            # Validate configuration
            Config.validate()
            print_success("Configuration validated")
            
            # Load data
            data_loader.load_data()
            print_success("Data loaded successfully")
            
            # Create agents
            print_info("Creating AI agents...")
            self.agents['orchestrator'] = create_orchestrator_agent()
            self.agents['query'] = create_query_agent()
            self.agents['suggester'] = create_action_suggester_agent()
            self.agents['executor'] = create_executor_agent()
            self.agents['reporter'] = create_report_generator_agent()
            print_success("AI agents created")
            
            # Create user proxy
            self.user_proxy = autogen.UserProxyAgent(
                name="User",
                human_input_mode="ALWAYS",
                max_consecutive_auto_reply=10,
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                code_execution_config=False,
            )
            
            self.initialized = True
            print_success("System initialized successfully\n")
            
        except FileNotFoundError as e:
            print_error(f"Data files not found: {e}")
            print_info("Please ensure Alert.xlsx and BOL.xlsx are in the data/ folder")
            return False
        except ValueError as e:
            print_error(f"Configuration error: {e}")
            print_info("Please check your .env file and API keys")
            return False
        except Exception as e:
            print_error(f"Initialization failed: {e}")
            return False
        
        return True
    
    def print_help(self):
        """Print help information"""
        help_text = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                      ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}📊 QUERY COMMANDS:{Style.RESET_ALL}
  • Show me alerts for [Customer] at [Facility]
  • Show me all BOL delayed by more than [X] hours
  • Show me high risk alerts (above 70%)
  • Show me alerts of type [Alert Type]
  • Show me alerts with less than [X] days left
  • What's the carrier performance?
  • Search for [keyword]

{Fore.YELLOW}💡 ACTION COMMANDS:{Style.RESET_ALL}
  • Suggest actions for these alerts
  • Stop alert for BOL [BOL number]
  • Add note to BOL [BOL number]: [your note]
  • Send email for BOL [BOL number]
  • Escalate BOL [BOL number]

{Fore.MAGENTA}📈 REPORT COMMANDS:{Style.RESET_ALL}
  • Generate daily summary report
  • Create report for [specific criteria]
  • Save report to file
  • Show action log

{Fore.BLUE}⚙️ SYSTEM COMMANDS:{Style.RESET_ALL}
  • help - Show this help message
  • status - Show system status
  • refresh - Reload data from files
  • memory - Show conversation history
  • clear - Clear conversation history
  • exit / quit - Exit the system

{Fore.CYAN}💬 EXAMPLES:{Style.RESET_ALL}
  User: "Show me alerts for Walmart at Palatka"
  User: "Show me all BOLs delayed by more than 12 hours"
  User: "Suggest actions for these alerts"
  User: "Stop alert for BOL10005 because issue resolved"
  User: "Generate daily summary report"
"""
        print(help_text)
    
    def print_status(self):
        """Print system status"""
        alert_count = len(data_loader.get_alert_data())
        bol_count = len(data_loader.get_bol_data())
        
        status = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║                     SYSTEM STATUS                          ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}✓{Style.RESET_ALL} System Initialized: {self.initialized}
{Fore.GREEN}✓{Style.RESET_ALL} Alerts Loaded: {alert_count}
{Fore.GREEN}✓{Style.RESET_ALL} BOL Records Loaded: {bol_count}
{Fore.GREEN}✓{Style.RESET_ALL} Active Agents: {len(self.agents)}
{Fore.GREEN}✓{Style.RESET_ALL} LLM Model: {Config.OPENAI_MODEL}
{Fore.GREEN}✓{Style.RESET_ALL} Memory Enabled: {Config.MEMORY_ENABLED}

{conversation_memory.get_conversation_summary()}
"""
        print(status)
    
    def start_conversation(self):
        """Start interactive conversation loop"""
        if not self.initialized:
            if not self.initialize():
                return
        
        print_welcome_banner()
        print_info("Welcome! I'm your OTIF Alert Management AI Assistant.")
        print_info("Type 'help' for available commands or start asking questions.")
        print_info("Type 'exit' or 'quit' to end the session.\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}You: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print_info("\nThank you for using OTIF Alert Management System!")
                    print_info("Goodbye! 👋\n")
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'status':
                    self.print_status()
                    continue
                
                elif user_input.lower() == 'refresh':
                    data_loader.refresh_data()
                    print_success("Data refreshed from source files")
                    continue
                
                elif user_input.lower() == 'memory':
                    print(conversation_memory.get_conversation_summary())
                    continue
                
                elif user_input.lower() == 'clear':
                    conversation_memory.clear()
                    print_success("Conversation history cleared")
                    continue
                
                # Add to conversation memory
                conversation_memory.add_message('user', user_input)
                
                # Route to orchestrator
                self.user_proxy.initiate_chat(
                    self.agents['orchestrator'],
                    message=user_input,
                )
                
            except KeyboardInterrupt:
                print_info("\n\nSession interrupted by user.")
                print_info("Type 'exit' to quit or continue chatting.\n")
                continue
            
            except Exception as e:
                print_error(f"Error processing request: {e}")
                print_info("Please try again or type 'help' for assistance.\n")
                continue

def main():
    """Main entry point"""
    system = OTIFAlertSystem()
    system.start_conversation()

if __name__ == "__main__":
    main()
