"""
Report generation functions
"""

import pandas as pd
from typing import Dict
from datetime import datetime
from tabulate import tabulate
from config import Config
import os

class ReportGenerator:
    """Generates reports for OTIF alerts"""
    
    def __init__(self):
        self.report_count = 0
    
    def generate_daily_alert_summary(self) -> str:
        """
        Generate daily alert summary report
        
        Returns:
            Formatted report string
        """
        from tools.data_loader import data_loader
        
        df = data_loader.get_combined_data()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Summary statistics
        total_alerts = len(df)
        high_risk = len(df[df['OTIF_Risk_Score'] > 0.7])
        delayed = len(df[df['No_of_Hours_Delayed'] > 0])
        
        # Alert type breakdown
        alert_type_counts = df['Alert_Type'].value_counts()
        
        # Delivery status breakdown
        delivery_status = df['Delivery_Status'].value_counts()
        
        # Top customers by alert count
        top_customers = df['Customer'].value_counts().head(5)
        
        # Top facilities by alert count
        top_facilities = df['Facility'].value_counts().head(5)
        
        # Build report
        report = f"""
╔════════════════════════════════════════════════════════════╗
║         OTIF ALERT MANAGEMENT - DAILY SUMMARY REPORT       ║
║                  {datetime.now().strftime('%B %d, %Y %H:%M')}                    ║
╚════════════════════════════════════════════════════════════╝

📊 OVERVIEW
───────────────────────────────────────────────────────────────
Total Active Alerts:        {total_alerts}
High Risk (>70%):          {high_risk} ({high_risk/total_alerts*100:.1f}%)
Delayed Shipments:         {delayed} ({delayed/total_alerts*100:.1f}%)

📋 ALERT TYPE DISTRIBUTION
───────────────────────────────────────────────────────────────
"""
        for alert_type, count in alert_type_counts.items():
            report += f"{alert_type:<40} {count:>5} ({count/total_alerts*100:>5.1f}%)\n"
        
        report += f"""
🚚 DELIVERY STATUS
───────────────────────────────────────────────────────────────
"""
        for status, count in delivery_status.items():
            report += f"{status:<20} {count:>5} ({count/total_alerts*100:>5.1f}%)\n"
        
        report += f"""
🏢 TOP 5 CUSTOMERS BY ALERT COUNT
───────────────────────────────────────────────────────────────
"""
        for customer, count in top_customers.items():
            report += f"{customer:<30} {count:>5}\n"
        
        report += f"""
🏭 TOP 5 FACILITIES BY ALERT COUNT
───────────────────────────────────────────────────────────────
"""
        for facility, count in top_facilities.items():
            report += f"{facility:<30} {count:>5}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
    
    def generate_detailed_alert_report(self, df: pd.DataFrame, title: str = "Alert Report") -> str:
        """
        Generate detailed report from dataframe
        
        Args:
            df: Dataframe with alert data
            title: Report title
        
        Returns:
            Formatted report string
        """
        if df.empty:
            return f"\n{title}\n{'='*60}\nNo alerts found matching criteria.\n"
        
        # Select key columns for display
        columns = [
            'BOL', 'Customer', 'Facility', 'Alert_Type', 
            'OTIF_Risk_Score', 'Days_Left_for_Delivery', 
            'Delivery_Status', 'No_of_Hours_Delayed'
        ]
        
        # Filter columns that exist
        available_cols = [col for col in columns if col in df.columns]
        display_df = df[available_cols].head(20)  # Limit to 20 rows for readability
        
        # Format report
        report = f"""
{title}
{'='*80}
Total Records: {len(df)}
Showing: {len(display_df)} records

{tabulate(display_df, headers='keys', tablefmt='grid', showindex=False)}

Summary Statistics:
- Average OTIF Risk Score: {df['OTIF_Risk_Score'].mean():.3f}
- Average Days Left: {df['Days_Left_for_Delivery'].mean():.1f} days
- Average Delay: {df['No_of_Hours_Delayed'].mean():.1f} hours
"""
        return report
    
    def save_report_to_file(self, report_content: str, filename: str = None) -> str:
        """
        Save report to file
        
        Args:
            report_content: Report text
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"OTIF_Report_{timestamp}.txt"
        
        filepath = os.path.join(Config.REPORT_OUTPUT_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.report_count += 1
        return filepath

# Global report generator instance
report_generator = ReportGenerator()

# Register functions
report_functions = {
    "generate_daily_alert_summary": report_generator.generate_daily_alert_summary,
    "generate_detailed_alert_report": report_generator.generate_detailed_alert_report,
    "save_report_to_file": report_generator.save_report_to_file,
}
