# embeddings_utils.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

def create_embeddings(
    text,
    chunk_size=1000,
    chunk_overlap=500,
    collection_name="policy_docs",
    persist_dir=None
):
    """
    Create embeddings entirely in memory (no disk writes).
    Works perfectly on Streamlit Cloud.
    """
    if not text or text.strip() == "":
        return None

    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        return None

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # ✅ Force in-memory mode (no SQLite persistence)
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        collection_name=collection_name,
        client_settings={"chromadb": {"anonymized_telemetry": False}},
        persist_directory=None
    )

    return vectordb


def clear_old_embeddings(persist_directory=None):
    """No-op function to avoid filesystem writes."""
    pass
