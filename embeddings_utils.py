# embeddings_utils.py
import os
import shutil
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


def create_embeddings(text, chunk_size=1000, chunk_overlap=500, collection_name=DEFAULT_COLLECTION_NAME, persist_dir=None):
    """
    Create a Chroma vectorstore for the given text in a dedicated folder.
    """
    if not text or text.strip() == "":
        return None

    # Use a separate folder per PDF to avoid collection conflicts
    if persist_dir is None:
        persist_dir = DEFAULT_PERSIST_DIR

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
        persist_directory=persist_dir,
        collection_name=collection_name
    )

    # Persist vectorstore
    vectordb.persist()
    return vectordb
