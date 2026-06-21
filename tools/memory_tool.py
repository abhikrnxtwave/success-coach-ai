from mem0 import MemoryClient
import os

try:
    import streamlit as st
except ImportError:
    st = None


def get_memory_client():

    api_key = None

    # Streamlit Cloud
    if st:
        try:
            api_key = st.secrets["MEM0_API_KEY"]
        except Exception:
            pass

    # Local (.env)
    if not api_key:
        api_key = os.getenv("MEM0_API_KEY")

    if not api_key:
        raise ValueError(
            "MEM0_API_KEY not found. "
            "Add it to .env locally or Streamlit Secrets."
        )

    return MemoryClient(
        api_key=api_key
    )


def save_memory(
    student_id,
    factual_memory,
    session_summary
):

    memory = get_memory_client()

    # Facts
    memory.add(
        messages=[
            {
                "role": "user",
                "content": factual_memory
            }
        ],
        user_id=student_id,
        metadata={
            "memory_type": "fact"
        }
    )

    # Summary
    memory.add(
        messages=[
            {
                "role": "user",
                "content": session_summary
            }
        ],
        user_id=student_id,
        metadata={
            "memory_type": "summary"
        }
    )


def search_memory(
    query,
    student_id
):

    memory = get_memory_client()

    results = memory.search(
        query=query,
        user_id=student_id
    )

    memory_text = ""

    for item in results:
        memory_text += (
            item.get(
                "memory",
                ""
            ) + "\n"
        )

    return memory_text