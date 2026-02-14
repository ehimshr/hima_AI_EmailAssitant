from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.core.state import AgentState

# Import specialized agents
from src.agents.input_parser import input_parser_agent
from src.agents.intent_detector import intent_detector_agent
from src.agents.personalization import personalization_agent
from src.agents.tone_stylist import tone_stylist_agent
from src.agents.draft_writer import draft_writer_agent
from src.agents.reviewer import review_validator_agent

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("input_parser", input_parser_agent)
    workflow.add_node("intent_detector", intent_detector_agent)
    workflow.add_node("personalization", personalization_agent)
    workflow.add_node("tone_stylist", tone_stylist_agent)
    workflow.add_node("draft_writer", draft_writer_agent)
    workflow.add_node("reviewer", review_validator_agent)
    
    # Set entry point
    workflow.set_entry_point("input_parser")
    
    # Add linear edges
    workflow.add_edge("input_parser", "intent_detector")
    workflow.add_edge("intent_detector", "personalization")
    workflow.add_edge("personalization", "tone_stylist")
    workflow.add_edge("tone_stylist", "draft_writer")
    
    workflow.add_edge("draft_writer", "reviewer")
    
    # Conditional edge for retry
    def should_retry(state):
        quality = state.get("quality")
        retry_count = state.get("retry_count", 0)
        
        if quality == "FAIL" and retry_count < 3:
            print(f"--- RETRYING ({retry_count}/3) ---")
            return "retry"
        return "end"

    workflow.add_conditional_edges(
        "reviewer",
        should_retry,
        {
            "retry": "draft_writer",
            "end": END
        }
    )
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
