"""
Action execution functions with LLM-powered note rephrasing and email generation
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime
from tools.data_loader import data_loader
from config import Config
import openai

class ActionExecutor:
    """Executes user-selected actions on alerts"""
    
    def __init__(self):
        self.action_log = []
        # Initialize OpenAI client
        openai.api_key = Config.OPENAI_API_KEY
    
    def rephrase_note_with_llm(self, note: str) -> str:
        """
        Rephrase user note using LLM for clarity and professionalism
        
        Args:
            note: Original user note
        
        Returns:
            Rephrased note
        """
        try:
            prompt = f"""Rephrase the following user note to be concise, professional, and clear. 
Keep it under 100 characters if possible. Maintain the key information.

Original note: {note}

Rephrased note:"""
            
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional business communication assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            rephrased = response.choices.message.content.strip()
            return rephrased
            
        except Exception as e:
            # If rephrasing fails, return original note
            print(f"Warning: Note rephrasing failed: {e}")
            return note
    
    def generate_email_body_with_llm(self, alert_data: Dict, escalate: bool = False) -> str:
        """
        Generate email body using LLM for professional communication
        
        Args:
            alert_data: Dictionary containing alert details
            escalate: Whether this is an escalation email
        
        Returns:
            Generated email body
        """
        try:
            escalation_text = "This is an ESCALATED alert requiring immediate attention." if escalate else ""
            
            prompt = f"""Generate a professional and concise email body for an OTIF (On-Time In-Full) delivery alert.

                    Alert Information:
                    - Customer: {alert_data['Customer']}
                    - Facility: {alert_data['Facility']}
                    - Alert Type: {alert_data['Alert_Type']}
                    - OTIF Risk Score: {alert_data['OTIF_Risk_Score']:.1%}
                    - Days Left for Delivery: {alert_data['Days_Left_for_Delivery']} days
                    - Delivery Status: {alert_data['Delivery_Status']}
                    - Hours Delayed: {alert_data['No_of_Hours_Delayed']} hours
                    - BOL Number: {alert_data['BOL']}

                    {escalation_text}

                    Write a professional email body that:
                    1. Clearly states the issue
                    2. Provides key metrics
                    3. Indicates urgency level
                    4. Requests appropriate action

                    Email body:"""
            
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional supply chain communication specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            email_body = response.choices.message.content.strip()
            return email_body
            
        except Exception as e:
            # If email generation fails, return formatted default template
            print(f"Warning: Email generation failed: {e}")
            return f"""
                    Alert Details:
                    - Customer: {alert_data['Customer']}
                    - Facility: {alert_data['Facility']}
                    - Alert Type: {alert_data['Alert_Type']}
                    - OTIF Risk Score: {alert_data['OTIF_Risk_Score']:.2%}
                    - Days Left: {alert_data['Days_Left_for_Delivery']} days
                    - Delivery Status: {alert_data['Delivery_Status']}
                    - Hours Delayed: {alert_data['No_of_Hours_Delayed']} hours

                    Action Required: Please review and take necessary action.
                    """
    
    def stop_alert(self, bol: str, reason: str = "") -> Dict:
        """
        Stop/suppress an alert
        
        Args:
            bol: Bill of Lading number
            reason: Reason for stopping alert
        
        Returns:
            Action result dictionary
        """
        try:
            df = data_loader.get_alert_data()
            
            if bol not in df['BOL'].values:
                return {
                    "success": False,
                    "message": f"BOL {bol} not found",
                    "bol": bol
                }
            
            # Update Stop_Alert column
            df.loc[df['BOL'] == bol, 'Stop_Alert'] = 'Yes'
            
            # Log action
            action = {
                "timestamp": datetime.now().isoformat(),
                "action": "stop_alert",
                "bol": bol,
                "reason": reason,
                "success": True
            }
            self.action_log.append(action)
            
            return {
                "success": True,
                "message": f"Alert for BOL {bol} has been stopped",
                "bol": bol,
                "reason": reason
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping alert: {str(e)}",
                "bol": bol
            }
    
    def add_note(self, bol: str, note: str) -> Dict:
        """
        Add note to an alert (with LLM rephrasing)
        
        Args:
            bol: Bill of Lading number
            note: Note text (will be rephrased by LLM)
        
        Returns:
            Action result dictionary
        """
        try:
            df = data_loader.get_alert_data()
            
            if bol not in df['BOL'].values:
                return {
                    "success": False,
                    "message": f"BOL {bol} not found",
                    "bol": bol
                }
            
            # Rephrase note using LLM for consistency and professionalism
            rephrased_note = self.rephrase_note_with_llm(note)
            
            # Update User_Notes column
            current_note = df.loc[df['BOL'] == bol, 'User_Notes'].values
            new_note = f"{current_note}; {rephrased_note}" if pd.notna(current_note) and current_note else rephrased_note
            
            df.loc[df['BOL'] == bol, 'User_Notes'] = new_note
            
            # Log action with both original and rephrased notes
            action = {
                "timestamp": datetime.now().isoformat(),
                "action": "add_note",
                "bol": bol,
                "original_note": note,
                "rephrased_note": rephrased_note,
                "success": True
            }
            self.action_log.append(action)
            
            return {
                "success": True,
                "message": f"Note added to BOL {bol}",
                "bol": bol,
                "original_note": note,
                "rephrased_note": rephrased_note
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding note: {str(e)}",
                "bol": bol
            }
    
    def send_email_alert(self, bol: str, escalate: bool = False) -> Dict:
        """
        Send email alert for a BOL (with LLM-generated email body)
        
        Args:
            bol: Bill of Lading number
            escalate: Whether to escalate to supervisor
        
        Returns:
            Action result dictionary
        """
        try:
            df = data_loader.get_combined_data()
            
            if bol not in df['BOL'].values:
                return {
                    "success": False,
                    "message": f"BOL {bol} not found",
                    "bol": bol
                }
            
            # Get alert details
            alert_row = df[df['BOL'] == bol].iloc
            
            # Prepare alert data dictionary
            alert_data = {
                'Customer': alert_row['Customer'],
                'Facility': alert_row['Facility'],
                'Alert_Type': alert_row['Alert_Type'],
                'OTIF_Risk_Score': alert_row['OTIF_Risk_Score'],
                'Days_Left_for_Delivery': alert_row['Days_Left_for_Delivery'],
                'Delivery_Status': alert_row['Delivery_Status'],
                'No_of_Hours_Delayed': alert_row['No_of_Hours_Delayed'],
                'BOL': bol
            }
            
            # Generate email body using LLM
            email_body = self.generate_email_body_with_llm(alert_data, escalate)
            
            email_details = {
                "to": alert_row['User_Email_ID'],
                "subject": f"{'[ESCALATED] ' if escalate else ''}OTIF Alert: {alert_row['Alert_Type']} - BOL {bol}",
                "body": email_body,
                "escalated": escalate
            }
            
            # Simulate email send (in production, integrate with email service)
            print(f"\n📧 EMAIL SENT:")
            print(f"To: {email_details['to']}")
            print(f"Subject: {email_details['subject']}")
            print(f"\nBody:\n{email_details['body']}")
            if escalate:
                print(f"\n⚠️  ESCALATED TO SUPERVISOR")
            
            # Log action
            action = {
                "timestamp": datetime.now().isoformat(),
                "action": "send_email",
                "bol": bol,
                "email": email_details,
                "escalated": escalate,
                "success": True
            }
            self.action_log.append(action)
            
            return {
                "success": True,
                "message": f"Email sent for BOL {bol}{' (ESCALATED)' if escalate else ''}",
                "bol": bol,
                "email_to": email_details['to']
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending email: {str(e)}",
                "bol": bol
            }
    
    def get_action_log(self) -> List[Dict]:
        """Get history of actions taken"""
        return self.action_log

# Global action executor instance
action_executor = ActionExecutor()

# Register functions
action_functions = {
    "stop_alert": action_executor.stop_alert,
    "add_note": action_executor.add_note,
    "send_email_alert": action_executor.send_email_alert,
    "get_action_log": action_executor.get_action_log,
}
