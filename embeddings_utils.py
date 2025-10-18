# embeddings_utils.py
import os
import shutil
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

# Use a temporary folder for Streamlit Cloud compatibility
PERSIST_DIR = os.path.join(tempfile.gettempdir(), "chroma_db_policy")
COLLECTION_NAME = "policy_docs"

def clear_old_embeddings():
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

    # Attempt to clear collection in memory if exists
    try:
        Chroma(persist_directory=PERSIST_DIR, collection_name=COLLECTION_NAME).delete_collection()
    except Exception:
        pass

def create_embeddings(text, chunk_size=1000, chunk_overlap=500, collection_name=COLLECTION_NAME):
    """
    Create a fresh Chroma vectorstore for the given text.
    Returns the vectorstore object or None if failed.
    """
    # Ensure no old persisted data remains
    clear_old_embeddings()

    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Safe collection name: alphanumeric only
    safe_collection_name = "".join(c for c in collection_name if c.isalnum() or c == "_")

    try:
        vectordb = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            persist_directory=PERSIST_DIR,
            collection_name=safe_collection_name
        )
        vectordb.persist()
        return vectordb
    except Exception as e:
        print(f"❌ Chroma vectorstore creation failed: {e}")
        return None
