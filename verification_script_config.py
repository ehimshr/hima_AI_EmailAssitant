import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import uuid

sys.path.append(os.getcwd())
from src.core.graph import create_graph

load_dotenv()
if not os.getenv("OPENAI_API_KEY"): sys.exit(0)

def test_config():
    print("Testing Dynamic LLM Configuration...")
    graph = create_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    # Test 1: GPT-3.5-Turbo with High Temp
    print("\n--- Test 1: GPT-3.5-Turbo (Temp 0.9) ---")
    inputs = {
        "messages": [HumanMessage(content="Write a short poem about coding.")],
        "user_info": {"profile": "default"},
        "model_config": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.9
        }
    }
    
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if "final_email" in value:
                 print(f"Final Output (GPT-3.5): {value['final_email'][:50]}...")
                 
    # Test 2: GPT-4o-mini with Low Temp (different model to ensure no crash)
    print("\n--- Test 2: GPT-4o-mini (Temp 0.0) ---")
    inputs["model_config"] = {"model": "gpt-4o-mini", "temperature": 0.0}
    
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if "final_email" in value:
                 print(f"Final Output (GPT-4o-mini): {value['final_email'][:50]}...")

    print("\nTest Passed: Graph executed with different configurations.")

if __name__ == "__main__":
    test_config()
