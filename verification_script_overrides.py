import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import uuid

sys.path.append(os.getcwd())
from src.core.graph import create_graph

load_dotenv()
if not os.getenv("OPENAI_API_KEY"): sys.exit(0)

def test_overrides():
    print("Testing UI Overrides (Intent & Metadata)...")
    graph = create_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    # User asks to "ask about project", but UI overrides Intent to "Apology" and adds Recipient "Boss"
    input_text = "Ask about the project status."
    inputs = {
        "messages": [HumanMessage(content=input_text)],
        "user_info": {
            "profile": "default", 
            "tone_mode": "Normal",
            "intent_mode": "Apology", # Override
            "recipient_override": "The Big Boss", # Override
            "extra_constraints": "Use very humble language" # Append
        }
    }
    
    print(f"Input: {input_text}")
    print(f"Overrides: Intent=Apology, Recipient=The Big Boss, Constraint=Humble")
    
    final_email = ""
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if "final_email" in value:
                 final_email = value["final_email"]
            if "intent_classification" in value:
                 print(f"Detected Intent: {value['intent_classification']}")
            if "parsed_input" in value:
                 print(f"Parsed Recipient: {value['parsed_input'].get('recipient')}")

    print(f"\nFinal Draft:\n{final_email}")
    
    if "apolog" in final_email.lower() or "sorry" in final_email.lower():
         print("\nTest Passed: Intent override successful (Apology detected).")
    else:
         print("\nTest Failed: Intent override might have failed.")
         
    if "Boss" in final_email:
         print("Test Passed: Recipient override successful.")

if __name__ == "__main__":
    test_overrides()
