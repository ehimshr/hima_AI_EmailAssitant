import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import uuid
import json

# Add src to path
sys.path.append(os.getcwd())

from src.core.graph import create_graph
from src.utils.learning import save_email_history, get_email_history

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("Skipping LLM test: OPENAI_API_KEY not found.")
    sys.exit(0)

def test_final_flow():
    print("Testing final flow with Learning & UI Tone Priority...")
    graph = create_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Simulate Learning
    print("\n--- 1. Simulating Learning ---")
    save_email_history(
        email_content="Hey there, just checking in on the project. Let me know!", 
        user_profile="default", 
        topic="Project Check-in"
    )
    history = get_email_history(limit=1)
    if history:
         print(f"History saved/retrieved successfully: {history[0]['content'][:20]}...")
    else:
         print("History save failed.")

    # 2. Test Tone (Assertive)
    print("\n--- 2. Testing Assertive Tone (UI Override) ---")
    input_text = "Ask for the overdue payment."
    inputs = {
        "messages": [HumanMessage(content=input_text)],
        "user_info": {"profile": "default", "tone_mode": "Assertive"}
    }
    
    final_email = ""
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if "final_email" in value:
                 final_email = value["final_email"]
                 
    print(f"Final Draft: {final_email[:100]}...")
    
    if "payment" in final_email.lower():
         print("Test Passed: Email generated.")
    else:
         print("Test Failed: Content mismatch.")

if __name__ == "__main__":
    test_final_flow()
