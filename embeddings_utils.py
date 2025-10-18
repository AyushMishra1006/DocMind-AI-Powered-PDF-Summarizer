# embeddings_utils.py
import os
import shutil
import tempfile
import hashlib
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

COLLECTION_PREFIX = "policy_docs"

def get_persist_dir(pdf_text):
    """Generate a unique temp folder per PDF for Streamlit Cloud."""
    pdf_hash = hashlib.sha256(pdf_text.encode()).hexdigest()[:8]
    folder = os.path.join(tempfile.gettempdir(), f"chroma_{pdf_hash}")
    os.makedirs(folder, exist_ok=True)
    return folder

def clear_old_embeddings(persist_dir, collection_name):
    """
    Fully clear persisted Chroma DB and any existing collection.
    """
    if os.path.exists(persist_dir):
        try:
            shutil.rmtree(persist_dir)
        except PermissionError:
            try:
                shutil.rmtree(persist_dir)
            except Exception:
                pass

    try:
        Chroma(persist_directory=persist_dir, collection_name=collection_name).delete_collection()
    except Exception:
        pass  # safe fallback

def create_embeddings(text, chunk_size=1000, chunk_overlap=500):
    """
    Create a fresh Chroma vectorstore for the given text.
    Returns the vectorstore or None if creation failed.
    """
    if not text.strip():
        print("❌ No text to create embeddings from.")
        return None

    persist_dir = get_persist_dir(text)
    collection_name = f"{COLLECTION_PREFIX}_{hashlib.sha256(text.encode()).hexdigest()[:8]}"

    # Clear any old embeddings in this folder
    clear_old_embeddings(persist_dir, collection_name)

    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta if c["content"].strip()]

    if not texts:
        print("❌ No valid text chunks extracted from PDF.")
        return None

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    try:
        vectordb = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_name=collection_name
        )
        vectordb.persist()
        return vectordb
    except Exception as e:
        print(f"❌ Chroma vectorstore creation failed: {e}")
        return None
