from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState


def draft_writer_agent(state: AgentState):
    """
    Generates main body text with structure and clarity.
    """
    print(f"--- DRAFT WRITER AGENT ---")
    parsed_input = state.get('parsed_input', {})
    intent = state.get('intent_classification', '')
    tone_instructions = state.get('tone_instructions', '')
    context = state.get('personalized_context', '')
    feedback = state.get('feedback', '')
    
    prompt_text = """
        You are an expert Ghostwriter.
        
        Task: Write an email based on the following:
        
        Topic: {topic}
        Recipient: {recipient}
        Intent: {intent}
        Constraints: {constraints}
        
        Sender Context:
        {context}
        
        Style Instructions:
        {style}
    """
    
    if feedback:
        prompt_text += f"\nPrevious Critique (Fix this): {feedback}\n"
        
    prompt_text += "\nWrite the email now. Return ONLY the email body."
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    
    # Get configuration
    config = state.get('model_config', {'model': 'gpt-4o-mini', 'temperature': 0.7})
    llm = get_llm(model=config['model'], temperature=config['temperature'])
    
    chain = prompt | llm | StrOutputParser()
    draft = chain.invoke({
        "topic": parsed_input.get("topic", ""),
        "recipient": parsed_input.get("recipient", ""),
        "intent": intent,
        "constraints": parsed_input.get("specific_constraints", ""),
        "context": context,
        "style": tone_instructions
    })
    
    return {"initial_draft": draft}
