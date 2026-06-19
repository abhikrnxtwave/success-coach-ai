import chromadb
from rag.ingest import build_knowledge_base
import os

from sentence_transformers import (
    SentenceTransformer
)

if not os.path.exists("chroma_db"):
    build_knowledge_base()

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    "knowledge_base"
)


def retrieve_context(
    query,
    top_k=3
):

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )

    docs = results["documents"][0]

    return "\n\n".join(docs)