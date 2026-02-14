from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState

llm = get_llm()

def intent_detector_agent(state: AgentState):
    """
    Classifies intent: outreach, follow-up, apology, info, reply, refine.
    """
    print(f"--- INTENT DETECTION AGENT ---")
    parsed_input = state.get('parsed_input', {})
    input_text = state['messages'][-1].content
    
    user_info = state.get('user_info', {})
    intent_mode = user_info.get('intent_mode', 'Auto')
    
    if intent_mode != "Auto":
        print(f"--- INTENT: OVERRIDE ({intent_mode}) ---")
        return {"intent_classification": intent_mode}
    
    prompt = ChatPromptTemplate.from_template(
        """
        Classify the intent of the following email request.
        Request: {input}
        Context (Topic): {topic}
        
        Choose ONE of the following categories:
        - Outreach (Cold email, introduction)
        - Follow-up (Chasing a response)
        - Reply (Responding to a received email)
        - Apology (Saying sorry)
        - Informational (Sharing updates)
        - Refine (Editing an existing draft)
        - Other
        
        Return ONLY the category name.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    classification = chain.invoke({
        "input": input_text,
        "topic": parsed_input.get("topic", "")
    })
    
    return {"intent_classification": classification.strip()}
