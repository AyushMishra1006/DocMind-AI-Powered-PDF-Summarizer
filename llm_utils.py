# llm_utils.py
import google.generativeai as genai
from embeddings_utils import create_embeddings

# NOTE: Move this to env vars before public deployment
API_KEY = "AIzaSyDIGQP1TtidfN9VGb888u8Ca6kYED6mwK8"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


class GeminiLLM:
    """Wrapper for Gemini 2.5 Flash via Google Generative AI."""
    def __init__(self, model):
        self.model = model

    def __call__(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text.strip() if response.text else ""


llm = GeminiLLM(model)


def ask_question(question, vectordb):
    """
    Query the vectordb retriever, build a context-aware OCR-safe prompt
    and call the LLM.

    Returns:
        (answer_text, docs_list)
    """
    if vectordb is None:
        raise ValueError(
            "Vectorstore not initialized. Create embeddings first by uploading a document."
        )

    # Retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": 20})

    # Defensive check
    if vectordb._collection.count() == 0:
        return "No embeddings found for this document. Please re-upload.", []

    docs = retriever.get_relevant_documents(question)
    if not docs:
        return "No relevant information found in the document.", []

    # Build context
    context = "\n\n".join(d.page_content for d in docs)

    # 🔥 OCR-AWARE PROMPT (KEY CHANGE)
    prompt = f"""
You are a highly intelligent document analysis assistant.

IMPORTANT CONTEXT:
- The document content below may come from OCR.
- OCR text can contain spelling mistakes, broken words, incorrect spacing,
  line breaks, or formatting issues.
- Your job is to intelligently reconstruct the intended meaning.
- Do NOT repeat OCR noise or raw artifacts.
- Rewrite and normalize the information in clear, professional language.
- If information is unclear, infer cautiously using surrounding context.
- Do NOT hallucinate facts that are not supported by the document.

📄 DOCUMENT CONTENT:
\"\"\"{context}\"\"\"


🎯 TASK:
- Carefully analyze all relevant document chunks.
- Combine information across chunks when needed.
- If multiple items exist (sections, points, entities, experiences, etc.),
  list ALL of them clearly.
- Produce a clean, human-readable final answer.

User Question:
{question}
"""

    response_text = llm(prompt)

    return (
        response_text or "The model did not return any output.",
        docs
    )
