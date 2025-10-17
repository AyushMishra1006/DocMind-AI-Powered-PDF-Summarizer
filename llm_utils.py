import google.generativeai as genai
import embeddings_utils  # import the module itself
from embeddings_utils import vectordb, create_embeddings


# 🔐 Gemini API Key
API_KEY = "AIzaSyDIGQP1TtidfN9VGb888u8Ca6kYED6mwK8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

class GeminiLLM:
    """Wrapper for Gemini 2.5 Flash via Google Generative AI."""
    def __init__(self, model):
        self.model = model

    def __call__(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text.strip()

llm = GeminiLLM(model)

def ask_question(question, vectordb):
    if vectordb is None:
        raise ValueError("Vectorstore not initialized. Create embeddings first.")

    retriever = vectordb.as_retriever(search_kwargs={"k": 100})
    docs = retriever.get_relevant_documents(question)
    if not docs:
        return "No relevant information found in the document.", []

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
    response_text = llm(prompt)
    return response_text or "The model did not return any output.", docs
