# rag/ingest.py

from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


def build_knowledge_base():

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(
        path="chroma_db"
    )

    collection = client.get_or_create_collection(
        name="knowledge_base"
    )

    knowledge_dir = Path("knowledge")

    for file in knowledge_dir.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        embedding = model.encode(
            text
        ).tolist()

        collection.add(
            ids=[file.stem],
            documents=[text],
            embeddings=[embedding]
        )

    print("Knowledge Base Indexed")


if __name__ == "__main__":
    build_knowledge_base()