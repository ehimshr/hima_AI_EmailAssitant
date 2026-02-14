from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")

def get_llm(model="gpt-4o-mini", temperature=0):
    """
    Returns a configured ChatOpenAI instance.
    """
    return ChatOpenAI(
        model=model,
        temperature=temperature
    )
