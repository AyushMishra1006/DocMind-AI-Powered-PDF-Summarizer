# embeddings_utils.py
import os
import shutil
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

PERSIST_DIR = "chroma_db_policy"
DEFAULT_COLLECTION_NAME = "policy_docs"

def clear_old_embeddings(collection_name=DEFAULT_COLLECTION_NAME):
    """
    Fully clear persisted Chroma DB and any existing collection.
    """
    # Remove on-disk data
    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except PermissionError:
            try:
                shutil.rmtree(PERSIST_DIR)
            except Exception:
                pass

    # Attempt to clear in-memory collection if exists
    try:
        Chroma(persist_directory=PERSIST_DIR, collection_name=collection_name).delete_collection()
    except Exception:
        # Safe fallback: collection may not exist yet
        pass


def create_embeddings(
    text, 
    chunk_size=1000, 
    chunk_overlap=500, 
    collection_name=DEFAULT_COLLECTION_NAME
):
    """
    Create a fresh Chroma vectorstore for the given text.
    """
    # Ensure no old persisted data remains
    clear_old_embeddings(collection_name=collection_name)

    # Split text into chunks with metadata
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Chroma vectorstore
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,               # ✅ Required
        persist_directory=PERSIST_DIR,
        collection_name=collection_name
    )

    # Persist to disk
    vectordb.persist()

    return vectordb
