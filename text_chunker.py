# text_chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text, chunk_size=1000, chunk_overlap=900):
    """
    Split long text into smaller chunks with basic cleaning.
    Returns a list of dicts: [{'content': chunk_text, 'metadata': {...}}, ...]
    """
    text = " ".join(text.split())  # remove extra whitespace/newlines

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    raw_chunks = splitter.split_text(text)

    # Add metadata (optional: page numbers or order)
    chunks = [{"content": c, "metadata": {"order": i}} for i, c in enumerate(raw_chunks)]
    return chunks

