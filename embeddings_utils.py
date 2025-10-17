import os
import shutil
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from text_chunker import chunk_text

vectordb = None
PERSIST_DIR = "chroma_db_policy"
COLLECTION_NAME = "policy_docs"

def clear_old_embeddings():
    global vectordb
    if vectordb:
        vectordb.delete_collection()
    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except PermissionError:
            pass
    vectordb = None

def create_embeddings(text, chunk_size=1000, chunk_overlap=500):
    global vectordb
    clear_old_embeddings()

    chunks_with_meta = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = [c["content"] for c in chunks_with_meta]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME
    )
    return vectordb
