import os
import hashlib
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

RAG_DB_PATH = "rag_db"
COLLECTION_NAME = "grade9_textbooks"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chroma_client = chromadb.PersistentClient(path=RAG_DB_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def make_id(text: str, metadata: dict) -> str:
    raw = text + str(metadata)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def create_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def add_textbook_content(
    text: str,
    subject: str,
    chapter: str,
    source_name: str,
    page_number: int | None = None
):
    chunks = chunk_text(text)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        metadata = {
            "subject": subject,
            "chapter": chapter,
            "source_name": source_name,
            "page_number": page_number or 0,
            "chunk_index": index
        }

        chunk_id = make_id(chunk, metadata)

        ids.append(chunk_id)
        documents.append(chunk)
        embeddings.append(create_embedding(chunk))
        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_textbook_content(query: str, subject: str, chapter: str, top_k: int = 5):
    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "$and": [
                {"subject": {"$eq": subject}},
                {"chapter": {"$eq": chapter}}
            ]
        }
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    return list(zip(docs, metas))
