"""
Query Agent - Responsible for data retrieval
"""

import autogen
from typing import Dict, List
from config import Config
from tools.query_functions import query_functions
from utils.formatters import format_dataframe_for_display

def create_query_agent():
    """Create and configure the Query Agent"""
    
    # System message defining agent role
    system_message = """You are the Query Agent for the OTIF Alert Management System.

Your responsibilities:
1. Understand user queries about alerts, BOLs, customers, facilities, carriers
2. Execute appropriate query functions to retrieve data
3. Format results in a clear, readable way
4. Handle ambiguous queries by asking clarifying questions

Available query functions:
- get_alerts_by_customer_facility(customer, facility, date)
- get_delayed_bols(min_hours)
- get_high_risk_alerts(risk_threshold)
- get_alerts_by_type(alert_type)
- get_alerts_by_days_left(max_days)
- get_delivery_status_summary()
- get_carrier_performance()
- search_alerts(query_text)

When user asks for alerts:
1. Identify which function to use based on the query
2. Extract parameters from the query
3. Execute the function
4. Present results in a clear table format
5. Provide summary statistics

Be concise but informative. Always confirm what you're searching for."""
    
    # Create agent
    query_agent = autogen.AssistantAgent(
        name="QueryAgent",
        system_message=system_message,
        llm_config=Config.get_llm_config(),
        human_input_mode="NEVER",
    )
    
    # Register query functions
    for func_name, func in query_functions.items():
        query_agent.register_function(
            function_map={func_name: func}
        )
    
    return query_agent
