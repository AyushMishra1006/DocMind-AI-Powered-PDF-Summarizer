# llm_utils.py
import google.generativeai as genai
from embeddings_utils import create_embeddings

# NOTE: It's strongly recommended to store API_KEY in env vars and load via os.getenv.
# For quick local testing you may keep it here, but don't commit keys to public repos.
API_KEY = "AIzaSyDIGQP1TtidfN9VGb888u8Ca6kYED6mwK8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

class GeminiLLM:
    """Wrapper for Gemini 2.5 Flash via Google Generative AI."""
    def __init__(self, model):
        self.model = model

    def __call__(self, prompt):
        # you may want to expand parameters (temperature, max output tokens, etc.) if needed
        response = self.model.generate_content(prompt)
        return response.text.strip()

llm = GeminiLLM(model)

def ask_question(question, vectordb):
    """
    Query the vectordb retriever, build a context prompt and call the LLM.
    Returns tuple (answer_text, docs_list).
    """
    if vectordb is None:
        raise ValueError("Vectorstore not initialized. Create embeddings first by uploading a PDF.")

    # Use retriever to pull relevant chunks
    retriever = vectordb.as_retriever(search_kwargs={"k": 20})
# Optional: defensive check
    if vectordb._collection.count() == 0:
        return "No embeddings found for this PDF. Please re-upload.", []




    docs = retriever.get_relevant_documents(question)
    if not docs:
        return "No relevant information found in the document.", []

    # Build context from retrieved docs
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"""
You are a highly intelligent assistant.
Analyze all document chunks below carefully before answering.

📄 DOCUMENT CONTENT:
\"\"\"{context}\"\"\"

🎯 TASK:
- Use all relevant information across chunks.
- If multiple items exist (projects, experiences, sections, or other details), list all of them clearly.

User Question: {question}
"""
    # Call the LLM wrapper
    response_text = llm(prompt)
    return (response_text or "The model did not return any output.", docs)
