from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.utils.llm import get_llm
from src.core.state import AgentState


def review_validator_agent(state: AgentState):
    """
    Checks grammar, tone accuracy, and ensures contextual coherence.
    Returns structured feedback.
    """
    print(f"--- REVIEW & VALIDATOR AGENT ---")
    draft = state.get('initial_draft', '')
    tone_instructions = state.get('tone_instructions', '')
    retry_count = state.get('retry_count', 0)
    
    prompt = ChatPromptTemplate.from_template(
        """
        Review the following email draft.
        
        Draft:
        {draft}
        
        Intended Style:
        {style}
        
        Check for:
        1. Grammar issues.
        2. Tone alignment (Does it match the intended style?).
        3. Clarity.
        
        Return a JSON object with:
        - quality: "PASS" or "FAIL" (Fail if it significantly misses the tone or has major errors)
        - critique: Brief explanation of issues (if any)
        - final_email: The corrected/improved email draft
        
        If it's a minor fix, mark as PASS and provide the fixed version.
        Only mark FAIL if it needs a complete rewrite from the writer.
        """
    )
    
    # Get configuration
    config = state.get('model_config', {'model': 'gpt-4o-mini', 'temperature': 0})
    llm = get_llm(model=config['model'], temperature=config['temperature'])
    
    chain = prompt | llm | JsonOutputParser()
    try:
        result = chain.invoke({
            "draft": draft,
            "style": tone_instructions
        })
    except Exception as e:
        print(f"Review parsing error: {e}")
        result = {"quality": "PASS", "critique": "Error parsing review", "final_email": draft}
    
    # Update retry count if failing
    if result.get("quality") == "FAIL":
        retry_count += 1
    
    return {
        "final_email": result.get("final_email"), 
        "critique": result.get("critique"),
        "feedback": result.get("critique"), # For the writer to see in next loop
        "retry_count": retry_count,
        "quality": result.get("quality") # Helper for graph edge
    }
