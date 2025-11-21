"""
Conversation memory management
"""

from typing import List, Dict
from datetime import datetime

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self.messages: List[Dict] = []
        self.session_start = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Add message to memory
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional metadata
        """
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # Trim if exceeds max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, n: int = 10) -> List[Dict]:
        """Get n most recent messages"""
        return self.messages[-n:]
    
    def get_all_messages(self) -> List[Dict]:
        """Get all messages"""
        return self.messages
    
    def search_messages(self, query: str) -> List[Dict]:
        """Search messages by content"""
        return [
            msg for msg in self.messages
            if query.lower() in msg['content'].lower()
        ]
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation"""
        user_messages = len([m for m in self.messages if m['role'] == 'user'])
        assistant_messages = len([m for m in self.messages if m['role'] == 'assistant'])
        
        return f"""
Conversation Summary:
- Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
- Total Messages: {len(self.messages)}
- User Messages: {user_messages}
- Assistant Messages: {assistant_messages}
- Duration: {(datetime.now() - self.session_start).seconds // 60} minutes
"""
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.session_start = datetime.now()

# Global conversation memory instance
conversation_memory = ConversationMemory()
