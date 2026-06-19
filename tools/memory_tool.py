from mem0 import MemoryClient
import os

memory = MemoryClient(
    api_key=os.getenv(
        "MEM0_API_KEY"
    )
)


def save_memory(
    student_id,
    factual_memory,
    session_summary
):

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



#Retrieve Memories from Mem0



def search_memory(
    query,
    student_id
):

    results = memory.search(
        query=query,
        filters={
            "user_id": student_id
        }
    )

    memory_text = ""

    memories = results.get(
        "results",
        []
    )

    for item in memories:

        memory_text += (
            item.get(
                "memory",
                ""
            ) + "\n"
        )

    return memory_text
