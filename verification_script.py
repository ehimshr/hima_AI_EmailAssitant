import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Add src to path
sys.path.append(os.getcwd())

from src.core.graph import create_graph

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("Skipping LLM test: OPENAI_API_KEY not found.")
    # Use a mock or just test graph structure
    print("Testing graph structure compilation...")
    try:
        graph = create_graph()
        print("Graph compiled successfully.")
    except Exception as e:
        print(f"Graph compilation failed: {e}")
    sys.exit(0)

def test_graph():
    print("Testing graph execution with LLM...")
    graph = create_graph()
    
    input_text = "Draft a professional email to invite John Doe to a podcast about AI."
    initial_state = {
        "messages": [HumanMessage(content=input_text)],
        "user_info": {"profile": "default"}
    }
    
    print(f"Input: {input_text}")
    try:
        final_state = graph.invoke(initial_state)
        print("\n--- Final State ---")
        print(f"Draft: {final_state.get('email_draft')}")
        print("Test Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_graph()
