from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    name: str
    email: str
    bio: str
    preferences: dict

class AgentState(TypedDict):
    """
    Represents the state of our graph.
    """
    messages: List[BaseMessage]
    user_info: Optional[dict] # Original simple storage
    
    # Specialized Agent Outputs
    parsed_input: Optional[dict]
    intent_classification: Optional[str]
    tone_instructions: Optional[str]
    personalized_context: Optional[str]
    initial_draft: Optional[str]
    critique: Optional[str]
    final_email: Optional[str]
    
    retry_count: int
    feedback: Optional[str]
    
    # Configuration
    model_config: dict
