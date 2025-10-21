# embeddings_utils.py
import os
import shutil
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

DEFAULT_COLLECTION_NAME = "policy_docs"

def clear_old_embeddings(persist_directory=None):
    """
    Remove existing persisted Chroma DB folder.
    """
    if persist_directory and os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
        except Exception:
            pass  # safe fallback

def create_embeddings(
    text,
    chunk_size=1000,
    chunk_overlap=500,
    collection_name=DEFAULT_COLLECTION_NAME,
    persist_dir=None
):
    """
    Create a Chroma vectorstore for the given text.
    Uses a temporary folder in Streamlit Cloud to avoid readonly DB errors.
    """
    if not text or text.strip() == "":
        return None

    # Use temp folder per PDF to avoid readonly DB errors
    if persist_dir is None:
        temp_folder = tempfile.gettempdir()
        persist_dir = os.path.join(temp_folder, f"{collection_name}_{hash(text) & 0xffffffff:x}")
        os.makedirs(persist_dir, exist_ok=True)

    # Clear previous embeddings in this folder only
    clear_old_embeddings(persist_directory=persist_dir)

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        return None

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Chroma vectorstore (in-memory if folder not writable)
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name
    )

    # Try to persist (ignore errors if folder is readonly)
    try:
        vectordb.persist()
    except Exception:
        pass

    return vectordb
