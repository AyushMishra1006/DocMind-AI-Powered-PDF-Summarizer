# embeddings_utils.py
import os
import shutil
import uuid
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

PERSIST_DIR = "chroma_db_policy"

def create_embeddings(text, chunk_size=1000, chunk_overlap=500):
    """
    Create a fresh Chroma vectorstore for the given text.
    Generates a unique collection name per upload to avoid conflicts.
    """
    # Generate a unique collection name for this upload
    collection_name = f"collection_{uuid.uuid4().hex[:8]}"

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name=collection_name
    )

    vectordb.persist()
    return vectordb, collection_name


def clear_all_collections():
    """
    Fully clear all persisted Chroma DB collections.
    """
    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except PermissionError:
            try:
                shutil.rmtree(PERSIST_DIR)
            except Exception:
                pass
