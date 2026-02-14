from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState


def tone_stylist_agent(state: AgentState):
    """
    Adjusts tone (formal, friendly, assertive, etc.) using tokenized prompts.
    """
    print(f"--- TONE STYLIST AGENT ---")
    parsed_input = state.get('parsed_input', {})
    intent = state.get('intent_classification', '')
    context = state.get('personalized_context', '')
    
    user_info = state.get('user_info', {})
    ui_tone = user_info.get('tone_mode', 'Normal')
    
    raw_request = parsed_input.get('raw_tone_request', 'None')
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a Tone Stylist.
        Context:
        {context}
        
        Intent: {intent}
        UI Selected Tone: {ui_tone}
        User Request Tone: {user_tone}
        
        Generate a concise set of style instructions for the writer.
        Prioritize the UI Selected Tone ({ui_tone}) as the primary mode.
        Define:
        1. Formality Level (1-10)
        2. Key adjectives (e.g., empathetic, direct)
        3. Structural guidance (e.g., use bullet points, keep paragraphs short)
        
        Return the instructions as a paragraph.
        """
    )
    
    # Get configuration
    config = state.get('model_config', {'model': 'gpt-4o-mini', 'temperature': 0.7})
    llm = get_llm(model=config['model'], temperature=config['temperature'])
    
    chain = prompt | llm | StrOutputParser()
    instructions = chain.invoke({
        "context": context,
        "intent": intent,
        "ui_tone": ui_tone,
        "user_tone": raw_request
    })
    
    return {"tone_instructions": instructions}
