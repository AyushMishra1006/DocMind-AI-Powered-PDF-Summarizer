import os
import shutil
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

PERSIST_DIR = "chroma_db_policy"
COLLECTION_NAME = "policy_docs"

def clear_old_embeddings(collection_name=COLLECTION_NAME):
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

    # Attempt to delete the collection if still open in memory
    try:
        Chroma(persist_directory=PERSIST_DIR, collection_name=collection_name).delete_collection()
    except Exception:
        pass

def create_embeddings(text, chunk_size=1000, chunk_overlap=500, collection_name=COLLECTION_NAME):
    """
    Create a fresh Chroma vectorstore for the given text.
    """
    if not text or text.strip() == "":
        # Defensive: empty input
        return None

    # Ensure no old persisted data remains
    clear_old_embeddings(collection_name=collection_name)

    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        # Defensive: no chunks extracted
        return None

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name=collection_name
    )

    # Persist to disk
    vectordb.persist()
    return vectordb
