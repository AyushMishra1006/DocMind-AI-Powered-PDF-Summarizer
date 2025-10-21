# embeddings_utils.py
import os
import shutil
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

DEFAULT_COLLECTION_NAME = "policy_docs"
DEFAULT_PERSIST_DIR = "chroma_db_policy"


def clear_old_embeddings(collection_name=DEFAULT_COLLECTION_NAME, persist_directory=None):
    """
    Fully clear persisted Chroma DB and any existing collection in the specified folder.
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
    If persist_dir is None, uses in-memory storage (avoids readonly DB errors in Streamlit Cloud).
    """
    if not text or text.strip() == "":
        return None

    # Use a temporary folder if none provided
    if persist_dir is None:
        # Use system temp folder for this PDF
        temp_folder = tempfile.gettempdir()
        persist_dir = os.path.join(temp_folder, f"{collection_name}_{hash(text) & 0xffffffff:x}")

    # Clear old embeddings in this folder only
    clear_old_embeddings(collection_name=collection_name, persist_directory=persist_dir)

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        return None

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Chroma vectorstore
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=persist_dir,  # can be None for in-memory
        collection_name=collection_name
    )

    # Persist only if folder is writable
    try:
        vectordb.persist()
    except Exception:
        pass  # ignore persistence errors in readonly environment

    return vectordb
