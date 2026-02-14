from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState
import json

llm = get_llm()

def input_parser_agent(state: AgentState):
    """
    Parses user input to determine intent and extract entities.
    """
    print(f"--- PARSING INPUT ---")
    messages = state['messages']
    last_message = messages[-1].content

    prompt = ChatPromptTemplate.from_template(
        """
        Analyze the following user request for an email assistant.
        Determine the intent (generate_email, reply_email, refine_email) and extract key information.
        
        User Request: {input}
        
        Return a JSON object with:
        - intent: One of [generate_email, reply_email, refine_email]
        - topic: Subject or topic of the email
        - recipient: Recipient name/email if available
        - tone: Desired tone if specified (e.g., professional, casual)
        - profile: The user profile to use (default to 'default' if not specified)
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    try:
        parsed_data = chain.invoke({"input": last_message})
    except Exception as e:
        print(f"Error parsing input: {e}")
        parsed_data = {"intent": "generate_email", "topic": last_message, "profile": "default"}
        
    return {"user_info": parsed_data, "next_step": parsed_data.get("intent")}

def email_generator_agent(state: AgentState):
    """
    Generates an email draft based on user info and profile.
    """
    print(f"--- GENERATING EMAIL ---")
    user_info = state['user_info']
    profile_name = user_info.get('profile', 'default')
    
    # Load profile data
    try:
        with open('src/data/user_profiles.json', 'r') as f:
            profiles = json.load(f)
            user_profile = profiles.get(profile_name, profiles['default'])
    except:
        user_profile = {"name": "User", "preferences": {"signature": "Best,\nUser"}}

    prompt = ChatPromptTemplate.from_template(
        """
        You are an AI email assistant acting on behalf of {name}.
        Bio: {bio}
        Preferences: Tone: {tone}, Signature: {signature}
        
        Task: Draft an email about '{topic}'.
        Recipient: {recipient}
        
        Ensure the email follows the user's preferences and bio.
        Return ONLY the email body.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    email_draft = chain.invoke({
        "name": user_profile['name'],
        "bio": user_profile['bio'],
        "tone": user_info.get('tone', user_profile['preferences']['tone']),
        "signature": user_profile['preferences']['signature'],
        "topic": user_info.get('topic', 'General'),
        "recipient": user_info.get('recipient', 'Undisclosed Recipient')
    })
    
    return {"email_draft": email_draft, "next_step": "end"}

def router_agent(state: AgentState):
    """
    Routes to the next agent based on intent.
    """
    print(f"--- ROUTING ---")
    intent = state.get('next_step')
    if intent == 'generate_email':
        return "email_generator"
    elif intent == 'reply_email':
        # For simplicity, route reply to generator for now, can be specialized later
        return "email_generator"
    elif intent == 'refine_email':
        return "email_generator" # Placeholder
    else:
        return "email_generator"
