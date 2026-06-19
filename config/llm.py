import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gpt-5"  # fallback if MODEL_NAME is not in .env
)

llm = ChatOpenAI(
    model=MODEL_NAME
)

def get_ai_response(messages):
    response = llm.invoke(messages)
    return response.content