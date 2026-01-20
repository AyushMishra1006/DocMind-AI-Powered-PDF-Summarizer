from llm_utils import llm

def generate_smart_questions(document_text, max_questions=6):
    """
    Generate smart, document-aware question suggestions.
    Called once per document upload.
    """
    if not document_text or len(document_text) < 100:
        return []

    prompt = f"""
You are an intelligent assistant helping users understand a document.

The document text below may come from OCR and may contain noise.
Your task is to generate useful, natural questions a user might ask
to understand this document better.

Rules:
- Do NOT answer the questions.
- Do NOT include numbering symbols like Q1, Q2.
- Return only short, clear questions.
- Avoid yes/no questions.
- Focus on summaries, key points, entities, dates, and structure.
- Avoid long or compound sentences.
- Be concise but meaningful.

DOCUMENT TEXT:
\"\"\"{document_text[:3000]}\"\"\"

Generate {max_questions} smart questions.
"""

    response = llm(prompt)

    # Post-process into clean list
    questions = []
    for line in response.split("\n"):
        line = line.strip("-• ").strip()
        if line.endswith("?"):
            questions.append(line)

    return questions[:max_questions]
