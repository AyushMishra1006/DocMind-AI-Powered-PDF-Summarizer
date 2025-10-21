# embeddings_utils.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

DEFAULT_COLLECTION_NAME = "policy_docs"


def create_embeddings(
    text,
    chunk_size=1000,
    chunk_overlap=500,
    collection_name=DEFAULT_COLLECTION_NAME,
):
    """
    Create an in-memory Chroma vectorstore for the given text.
    Fully avoids readonly database errors in Streamlit Cloud.
    """
    if not text or text.strip() == "":
        return None

    # Split text into chunks
    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    if not texts:
        return None

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create in-memory Chroma vectorstore (persist_directory=None)
    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        collection_name=collection_name,  # can be unique per PDF if needed
        persist_directory=None  # IMPORTANT: fully in-memory
    )

    return vectordb
