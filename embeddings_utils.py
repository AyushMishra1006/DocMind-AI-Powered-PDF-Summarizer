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
    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except PermissionError:
            try:
                shutil.rmtree(PERSIST_DIR)
            except Exception:
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
    clear_old_embeddings(collection_name=collection_name)

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # ⚠️ Pass the embeddings object itself, not embed_query
    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,  # correct: object with embed_documents()
        persist_directory=PERSIST_DIR
    )

    # Add texts
    vectordb.add_texts(texts)

    # Persist
    vectordb.persist()

    return vectordb
