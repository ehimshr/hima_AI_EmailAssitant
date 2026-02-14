import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import uuid

# Add src to path
sys.path.append(os.getcwd())

from src.core.graph import create_graph

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("Skipping LLM test: OPENAI_API_KEY not found.")
    sys.exit(0)

def test_memory():
    print("Testing graph execution with Memory (Thread persistence)...")
    graph = create_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Step 1: Initial Draft
    input_text = "Draft a short email to Alice about the meeting tomorrow at 2 PM."
    inputs = {
        "messages": [HumanMessage(content=input_text)],
        "user_info": {"profile": "default"}
    }
    
    print(f"\n--- Step 1: Input: {input_text} ---")
    final_email_1 = ""
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if "email_draft" in value:
                 final_email_1 = value["email_draft"]
                 
    print(f"Draft 1: {final_email_1}")
    
    # Step 2: Refinement (Should use context)
    refine_text = "Make it more formal."
    inputs_2 = {
        "messages": [HumanMessage(content=refine_text)]
    }
    
    print(f"\n--- Step 2: Refinement Input: {refine_text} ---")
    final_email_2 = ""
    for event in graph.stream(inputs_2, config=config):
        for key, value in event.items():
            if "email_draft" in value:
                 final_email_2 = value["email_draft"]
                 
    print(f"Draft 2: {final_email_2}")
    
    if final_email_1 and final_email_2 and final_email_1 != final_email_2:
        print("\nTest Passed: Memory utilized, draft updated.")
    else:
        print("\nTest Failed: Drafts might be same or empty.")

if __name__ == "__main__":
    test_memory()
