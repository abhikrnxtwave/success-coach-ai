from tools.memory_tool import memory


def get_student_memory(
    student_id
):

    try:

        memories = memory.search(
            query="student profile",
            user_id=student_id
        )

        return memories

    except:

        return []