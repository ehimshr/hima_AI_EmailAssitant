from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState

llm = get_llm()

def input_parser_agent(state: AgentState):
    """
    Validates prompt, extracts output, recipient, tone, constraints.
    """
    print(f"--- INPUT PARSER AGENT ---")
    messages = state['messages']
    last_message = messages[-1].content

    prompt = ChatPromptTemplate.from_template(
        """
        Analyze the following user request for an email assistant.
        Extract the following structured information:
        
        User Request: {input}
        
        Return a JSON object with:
        - topic: The main subject/topic
        - recipient: Name or email of recipient (or "Unknown")
        - specific_constraints: Any specific constraints mentioned (e.g., "short", "no emojis")
        - raw_tone_request: Any specific tone requested by user (e.g., "friendly", "stern")
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    try:
        parsed_data = chain.invoke({"input": last_message})
    except Exception as e:
        print(f"Error parsing input: {e}")
        parsed_data = {
            "topic": last_message,
            "recipient": "Unknown",
            "specific_constraints": "None",
            "raw_tone_request": "None"
        }
        
    # Merge UI overrides
    user_info = state.get('user_info', {})
    if user_info.get('recipient_override'):
        parsed_data['recipient'] = user_info['recipient_override']
    
    if user_info.get('extra_constraints'):
        current_constraints = parsed_data.get('specific_constraints', 'None')
        parsed_data['specific_constraints'] = f"{current_constraints}. {user_info['extra_constraints']}"
        
    return {"parsed_input": parsed_data}
