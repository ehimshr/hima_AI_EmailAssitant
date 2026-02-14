import json
import os
from datetime import datetime

HISTORY_FILE = 'src/data/email_history.json'

def save_email_history(email_content, user_profile, topic):
    """
    Saves the finalized email to a history file for future learning.
    """
    if not os.path.exists('src/data'):
        os.makedirs('src/data')
        
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
            
    entry = {
        "timestamp": datetime.now().isoformat(),
        "profile": user_profile,
        "topic": topic,
        "content": email_content
    }
    
    history.append(entry)
    
    # Keep last 50
    if len(history) > 50:
        history = history[-50:]
        
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_email_history(limit=5):
    """
    Retrieves recent email history to use as context.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
        
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        return history[-limit:]
    except:
        return []
