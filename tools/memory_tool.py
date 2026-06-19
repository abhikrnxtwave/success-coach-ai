from mem0 import MemoryClient
import os

memory = MemoryClient(
    api_key=os.getenv(
        "MEM0_API_KEY"
    )
)


def save_memory(
    student_id,
    conversation
):

    memory.add(
        messages=[
            {
                "role": "user",
                "content": conversation
            }
        ],
        user_id=student_id
    )