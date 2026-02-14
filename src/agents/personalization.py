import json
from src.core.state import AgentState
from src.utils.learning import get_email_history

def personalization_agent(state: AgentState):
    """
    Injects user profile data and prior messages (context).
    """
    print(f"--- PERSONALIZATION AGENT ---")
    user_info = state.get('user_info', {})
    profile_name = user_info.get('profile', 'default')
    
    # Load profile data
    try:
        with open('src/data/user_profiles.json', 'r') as f:
            profiles = json.load(f)
            user_profile = profiles.get(profile_name, profiles['default'])
    except:
        user_profile = {
            "name": "User", 
            "bio": "Unknown",
            "preferences": {"tone": "neutral", "signature": "Best,\nUser"}
        }
        
    # Get recent history
    history = get_email_history(limit=3)
    history_str = ""
    if history:
        history_str = "\nRecent Emails for Style Reference:\n"
        for h in history:
            history_str += f"- Topic: {h.get('topic')}\n  Content: {h.get('content')[:200]}...\n"
    
    context_str = f"""
    Sender Name: {user_profile['name']}
    Sender Bio: {user_profile['bio']}
    Base Tone Preference: {user_profile['preferences']['tone']}
    Signature: {user_profile['preferences']['signature']}
    
    {history_str}
    """
    
    return {"personalized_context": context_str}
