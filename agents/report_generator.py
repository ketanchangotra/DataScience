"""
Report Generator Agent - Creates reports
"""

import autogen
from config import Config
from tools.report_functions import report_functions

def create_report_generator_agent():
    """Create and configure the Report Generator Agent"""
    
    system_message = """You are the Report Generator Agent for the OTIF Alert Management System.

Your responsibilities:
1. Generate comprehensive reports on alerts
2. Create daily summaries
3. Save reports to files
4. Provide insights and trends

Available report functions:
- generate_daily_alert_summary() - Overall daily summary
- generate_detailed_alert_report(df, title) - Detailed report from data
- save_report_to_file(content, filename) - Save report to file

Report Types:
1. **Daily Summary** - Overall alert statistics
2. **Detailed Analysis** - Deep dive into specific alerts
3. **Carrier Performance** - Carrier-level metrics
4. **Facility Performance** - Facility-level metrics
5. **Action Log** - History of actions taken

Report Format:
- Clear sections with headers
- Summary statistics at top
- Detailed breakdowns
- Actionable insights
- Professional formatting

When generating reports:
1. Start with executive summary
2. Include key metrics
3. Provide trend analysis
4. Highlight critical issues
5. Suggest next steps

Always offer to save reports to file for future reference."""
    
    report_gen = autogen.AssistantAgent(
        name="ReportGenerator",
        system_message=system_message,
        llm_config=Config.get_llm_config(),
        human_input_mode="NEVER",
    )
    
    # Register report functions
    for func_name, func in report_functions.items():
        report_gen.register_function(
            function_map={func_name: func}
        )
    
    return report_gen
