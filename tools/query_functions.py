"""
Query execution functions for data retrieval
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta
from tools.data_loader import data_loader

def get_alerts_by_customer_facility(customer: str, facility: str, date: str = "today") -> pd.DataFrame:
    """
    Get alerts for specific customer and facility
    
    Args:
        customer: Customer name
        facility: Facility name
        date: Date filter ("today", "yesterday", or YYYY-MM-DD)
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    
    # Filter by customer and facility
    result = df[
        (df['Customer'].str.contains(customer, case=False, na=False)) &
        (df['Facility'].str.contains(facility, case=False, na=False))
    ]
    
    # Apply date filter if needed
    if date.lower() == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        result = result[result['Alert_Start_Date'] == today]
    elif date.lower() == "yesterday":
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        result = result[result['Alert_Start_Date'] == yesterday]
    
    return result

def get_delayed_bols(min_hours: int = 12) -> pd.DataFrame:
    """
    Get all BOLs delayed by more than specified hours
    
    Args:
        min_hours: Minimum delay hours
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    result = df[df['No_of_Hours_Delayed'] > min_hours]
    return result.sort_values('No_of_Hours_Delayed', ascending=False)

def get_high_risk_alerts(risk_threshold: float = 0.7) -> pd.DataFrame:
    """
    Get alerts with OTIF risk score above threshold
    
    Args:
        risk_threshold: Minimum risk score (0-1)
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    result = df[df['OTIF_Risk_Score'] >= risk_threshold]
    return result.sort_values('OTIF_Risk_Score', ascending=False)

def get_alerts_by_type(alert_type: str) -> pd.DataFrame:
    """
    Get alerts by alert type
    
    Args:
        alert_type: Type of alert
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    result = df[df['Alert_Type'].str.contains(alert_type, case=False, na=False)]
    return result

def get_alerts_by_days_left(max_days: int = 5) -> pd.DataFrame:
    """
    Get alerts with limited days left for delivery
    
    Args:
        max_days: Maximum days left
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    result = df[df['Days_Left_for_Delivery'] <= max_days]
    return result.sort_values('Days_Left_for_Delivery')

def get_delivery_status_summary() -> Dict[str, int]:
    """
    Get summary of delivery statuses
    
    Returns:
        Dictionary with status counts
    """
    df = data_loader.get_bol_data()
    return df['Delivery_Status'].value_counts().to_dict()

def get_carrier_performance() -> pd.DataFrame:
    """
    Get carrier performance metrics
    
    Returns:
        Dataframe with carrier metrics
    """
    df = data_loader.get_combined_data()
    
    carrier_stats = df.groupby('Carrier_Name_bol').agg({
        'BOL': 'count',
        'No_of_Hours_Delayed': 'mean',
        'Delivery_Status': lambda x: (x == 'On Time').sum()
    }).reset_index()
    
    carrier_stats.columns = ['Carrier', 'Total_Shipments', 'Avg_Delay_Hours', 'On_Time_Count']
    carrier_stats['On_Time_Rate_%'] = (
        carrier_stats['On_Time_Count'] / carrier_stats['Total_Shipments'] * 100
    ).round(1)
    
    return carrier_stats.sort_values('Avg_Delay_Hours', ascending=False)

def search_alerts(query_text: str) -> pd.DataFrame:
    """
    Search alerts using free text
    
    Args:
        query_text: Search text
    
    Returns:
        Filtered dataframe
    """
    df = data_loader.get_combined_data()
    
    # Search across multiple columns
    mask = (
        df['Customer'].str.contains(query_text, case=False, na=False) |
        df['Facility'].str.contains(query_text, case=False, na=False) |
        df['Alert_Type'].str.contains(query_text, case=False, na=False) |
        df['Material_Name'].str.contains(query_text, case=False, na=False)
    )
    
    return df[mask]

# Register functions for AutoGen
query_functions = {
    "get_alerts_by_customer_facility": get_alerts_by_customer_facility,
    "get_delayed_bols": get_delayed_bols,
    "get_high_risk_alerts": get_high_risk_alerts,
    "get_alerts_by_type": get_alerts_by_type,
    "get_alerts_by_days_left": get_alerts_by_days_left,
    "get_delivery_status_summary": get_delivery_status_summary,
    "get_carrier_performance": get_carrier_performance,
    "search_alerts": search_alerts,
}
