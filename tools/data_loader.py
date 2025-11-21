"""
Data loading and management utilities
"""

import pandas as pd
from typing import Tuple, Optional
from config import Config

class DataLoader:
    """Loads and manages Alert and BOL data"""
    
    def __init__(self):
        self.alert_df: Optional[pd.DataFrame] = None
        self.bol_df: Optional[pd.DataFrame] = None
        self.combined_df: Optional[pd.DataFrame] = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load Alert.xlsx and BOL.xlsx files"""
        try:
            # Load Alert data
            self.alert_df = pd.read_excel(Config.ALERT_FILE)
            print(f"✓ Loaded Alert.xlsx: {len(self.alert_df)} records")
            
            # Load BOL data
            self.bol_df = pd.read_excel(Config.BOL_FILE)
            print(f"✓ Loaded BOL.xlsx: {len(self.bol_df)} records")
            
            # Create combined view
            self.combined_df = self.alert_df.merge(
                self.bol_df, 
                on='BOL', 
                how='inner',
                suffixes=('_alert', '_bol')
            )
            print(f"✓ Created combined view: {len(self.combined_df)} records")
            
            return self.alert_df, self.bol_df, self.combined_df
            
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Data files not found. Please ensure Alert.xlsx and BOL.xlsx "
                f"are in the {Config.DATA_FOLDER} folder."
            ) from e
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}") from e
    
    def get_alert_data(self) -> pd.DataFrame:
        """Get Alert dataframe"""
        if self.alert_df is None:
            self.load_data()
        return self.alert_df
    
    def get_bol_data(self) -> pd.DataFrame:
        """Get BOL dataframe"""
        if self.bol_df is None:
            self.load_data()
        return self.bol_df
    
    def get_combined_data(self) -> pd.DataFrame:
        """Get combined dataframe"""
        if self.combined_df is None:
            self.load_data()
        return self.combined_df
    
    def refresh_data(self):
        """Reload data from files"""
        self.load_data()
        print("✓ Data refreshed from source files")

# Global data loader instance
data_loader = DataLoader()
