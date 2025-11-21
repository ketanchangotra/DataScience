"""
Executor Agent - Executes user-selected actions
"""

import autogen
from config import Config
from tools.action_functions import action_functions

def create_executor_agent():
    """Create and configure the Executor Agent"""
    
    system_message = """You are the Executor Agent for the OTIF Alert Management System.

Your responsibilities:
1. Execute actions selected by the user
2. Confirm action completion
3. Log all actions taken
4. Handle errors gracefully

Available actions:
- stop_alert(bol, reason) - Stop/suppress an alert
- add_note(bol, note) - Add note to alert
- send_email_alert(bol, escalate) - Send email notification
- get_action_log() - View action history

Execution Process:
1. Confirm the action with user
2. Execute the action function
3. Report success or failure
4. Suggest next steps if appropriate

After executing actions:
- Confirm what was done
- Show updated status
- Ask if user wants to take more actions

Always confirm successful execution and handle errors professionally."""
    
    executor = autogen.AssistantAgent(
        name="ExecutorAgent",
        system_message=system_message,
        llm_config=Config.get_llm_config(),
        human_input_mode="NEVER",
    )
    
    # Register action functions
    for func_name, func in action_functions.items():
        executor.register_function(
            function_map={func_name: func}
        )
    
    return executor
