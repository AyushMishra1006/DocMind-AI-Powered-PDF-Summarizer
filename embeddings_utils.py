# embeddings_utils.py
import os
import shutil
import uuid
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

PERSIST_DIR = "chroma_db_policy"

def clear_old_embeddings():
    """
    Fully clear persisted Chroma DB to avoid collection conflicts.
    """
    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except PermissionError:
            try:
                shutil.rmtree(PERSIST_DIR)
            except Exception:
                pass

def create_embeddings(text, chunk_size=1000, chunk_overlap=500, collection_name=None):
    """
    Create a Chroma vectorstore for the given text.
    Each upload uses a unique collection name if not provided.
    """
    if collection_name is None:
        collection_name = f"collection_{uuid.uuid4().hex[:8]}"

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create a new vectorstore safely
    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )

    # Add texts
    vectordb.add_texts(texts)

    # Persist to disk
    vectordb.persist()

    return vectordb, collection_name
