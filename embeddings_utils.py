# embeddings_utils.py
import os
import shutil
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

# Use Streamlit Cloud-friendly temporary folder
PERSIST_DIR = os.path.join(tempfile.gettempdir(), "chroma_db_policy")
os.makedirs(PERSIST_DIR, exist_ok=True)  # ensure folder exists

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

    # Explicitly clear collection if still open in memory
    try:
        Chroma(persist_directory=PERSIST_DIR, collection_name=COLLECTION_NAME).delete_collection()
    except Exception:
        pass  # safe fallback

def create_embeddings(text, chunk_size=1000, chunk_overlap=500, collection_name=COLLECTION_NAME):
    """
    Create a fresh Chroma vectorstore for the given text.
    Returns the vectorstore or None if creation failed.
    """
    # Clear old persisted data
    clear_old_embeddings()

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        print("❌ No text chunks extracted from PDF.")
        return None

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Ensure collection name is safe for Chroma
    safe_collection_name = "".join(c for c in collection_name if c.isalnum() or c == "_")

    # Try creating the vectorstore with a retry
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
        # Retry once
        try:
            vectordb = Chroma.from_texts(
                texts=texts,
                embedding=embeddings,
                persist_directory=PERSIST_DIR,
                collection_name=safe_collection_name
            )
            vectordb.persist()
            return vectordb
        except Exception as e2:
            print(f"❌ Chroma retry failed: {e2}")
            return None
