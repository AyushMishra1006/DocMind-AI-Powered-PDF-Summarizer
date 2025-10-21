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
    Safe for Streamlit Cloud deployment.
    """
    if not text or text.strip() == "":
        return None

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        return None

    # Initialize embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create in-memory Chroma (NO persist_directory)
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        collection_name=collection_name
    )

    # Do NOT persist — in-memory only
    return vectordb
