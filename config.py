
"""
Configuration settings for OTIF Alert Management System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Data Paths
    DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")
    ALERT_FILE = os.path.join(DATA_FOLDER, "Alert.xlsx")
    BOL_FILE = os.path.join(DATA_FOLDER, "BOL.xlsx")
    
    # Agent Configuration
    MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", 50))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.1))
    
    # Memory Configuration
    MEMORY_ENABLED = True
    MEMORY_MAX_MESSAGES = 100
    
    # Report Configuration
    REPORT_OUTPUT_FOLDER = "./reports"
    
    @staticmethod
    def get_llm_config():
        """Get LLM configuration for AutoGen"""
        return {
            "config_list": [
                {
                    "model": Config.OPENAI_MODEL,
                    "api_key": Config.OPENAI_API_KEY,
                    "temperature": Config.TEMPERATURE,
                }
            ],
            "timeout": 120,
        }
    
    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found in .env file. "
                "Please add your API key to continue."
            )
        
        if not os.path.exists(Config.DATA_FOLDER):
            os.makedirs(Config.DATA_FOLDER)
            print(f"Created data folder: {Config.DATA_FOLDER}")
        
        if not os.path.exists(Config.REPORT_OUTPUT_FOLDER):
            os.makedirs(Config.REPORT_OUTPUT_FOLDER)
            print(f"Created reports folder: {Config.REPORT_OUTPUT_FOLDER}")

