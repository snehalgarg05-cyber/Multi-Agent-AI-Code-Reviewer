import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq


def get_llm(temperature: float = 0.3):
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=2000,
    )
